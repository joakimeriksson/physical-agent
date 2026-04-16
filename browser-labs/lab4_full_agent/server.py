#!/usr/bin/env python3
"""Full Agent Server - bridges browser UI to Ollama and Dirigera MCP.

The browser handles camera, microphone, and UI.
This server handles LLM calls and IoT device control.

Usage:
    uv run python server.py
    uv run python server.py --port 9090
"""

import argparse
import json
import re
import os
import httpx
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
import uvicorn

# --- Configuration (loaded from ../config.json) ---

CONFIG = {}

def load_config():
    global CONFIG
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    try:
        with open(config_path) as f:
            CONFIG = json.load(f)
    except FileNotFoundError:
        print(f"Warning: {config_path} not found, using defaults")
        CONFIG = {
            "llm_url": "https://ollama.botbox.se/v1",
            "llm_api_key": "",
            "mcp_url": "https://dirigera.botbox.se",
            "mcp_api_key": "",
            "chat_model": "gemma4:e2b",
            "vision_model": "gemma3:latest",
        }

# --- MCP Client (handles sessions, JWT, SSE parsing) ---

class MCPClient:
    def __init__(self, mcp_url, api_key):
        self.mcp_url = mcp_url.rstrip("/")
        self.api_key = api_key
        self.token = None
        self.session_id = None
        self.call_id = 0
        self.tools = None  # cached OpenAI-format tools from MCP

    async def _get_token(self):
        if self.token:
            return self.token
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{self.mcp_url}/auth/token",
                json={"api_key": self.api_key})
            resp.raise_for_status()
            self.token = resp.json()["token"]
            return self.token

    async def _init_session(self):
        token = await self._get_token()
        self.call_id += 1
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{self.mcp_url}/mcp",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "Authorization": f"Bearer {token}",
                },
                json={
                    "jsonrpc": "2.0", "id": self.call_id, "method": "initialize",
                    "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                               "clientInfo": {"name": "lab4-server", "version": "1.0"}}
                })
            self.session_id = resp.headers.get("mcp-session-id")

    async def _send_mcp(self, method, params=None):
        """Send a JSON-RPC request to the MCP server and parse the response."""
        if not self.session_id:
            await self._init_session()

        token = await self._get_token()
        self.call_id += 1
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{self.mcp_url}/mcp",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "Authorization": f"Bearer {token}",
                    "Mcp-Session-Id": self.session_id,
                },
                json={
                    "jsonrpc": "2.0", "id": self.call_id, "method": method,
                    "params": params or {}
                })

        # Handle session expiry
        if resp.status_code in (404, 400):
            self.session_id = None
            self.tools = None
            return await self._send_mcp(method, params)

        def _extract(data):
            if not isinstance(data, dict):
                return None
            if "result" in data:
                return ("result", data["result"])
            if "error" in data:
                err = data["error"]
                msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
                return ("error", msg)
            return None

        # Parse SSE or JSON response
        text = resp.text
        for line in text.split("\n"):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                except json.JSONDecodeError:
                    continue
                parsed = _extract(data)
                if parsed and parsed[0] == "result":
                    return parsed[1]
                if parsed and parsed[0] == "error":
                    raise Exception(parsed[1])
        # Try direct JSON
        try:
            data = resp.json()
        except Exception:
            raise Exception(f"Unexpected MCP response ({resp.status_code}): {text[:200]}")
        parsed = _extract(data)
        if parsed and parsed[0] == "result":
            return parsed[1]
        if parsed and parsed[0] == "error":
            raise Exception(parsed[1])
        raise Exception(f"Unexpected MCP response: {str(data)[:200]}")

    async def list_tools(self):
        """Fetch tools from MCP and convert to OpenAI function-calling format."""
        if self.tools is not None:
            return self.tools

        result = await self._send_mcp("tools/list")
        mcp_tools = result.get("tools", [])
        self.tools = []
        for t in mcp_tools:
            # Convert MCP inputSchema to OpenAI parameters format
            params = dict(t.get("inputSchema", {"type": "object", "properties": {}}))
            # Remove fields that some LLM providers (e.g. Ollama) don't accept
            params.pop("additionalProperties", None)
            params.pop("$schema", None)
            self.tools.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": params,
                }
            })
        print(f"Loaded {len(self.tools)} tools from MCP: {[t['function']['name'] for t in self.tools]}")
        return self.tools

    async def call_tool(self, tool_name, arguments=None):
        """Call an MCP tool. Returns the parsed result."""
        result = await self._send_mcp("tools/call", {"name": tool_name, "arguments": arguments or {}})
        if "structuredContent" in result:
            return result["structuredContent"]["result"]
        if "content" in result:
            return json.loads(result["content"][0]["text"])
        return result

mcp = None

# --- LLM Client (OpenAI-compatible — works with Ollama, Groq, OpenAI, etc.) ---

async def llm_chat(messages, tools=None, model=None, images=None):
    """Chat with any OpenAI-compatible API. Returns the response message dict."""
    url = CONFIG.get("llm_url", "").rstrip("/")
    api_key = CONFIG.get("llm_api_key", "")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model or CONFIG.get("chat_model", "qwen3:4b"),
        "messages": messages,
    }
    if tools and not images:
        payload["tools"] = tools
    if images:
        payload["model"] = model or CONFIG.get("vision_model", payload["model"])
        for msg in reversed(payload["messages"]):
            if msg["role"] == "user":
                msg["content"] = [
                    {"type": "text", "text": msg["content"]},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{images[0]}"}},
                ]
                break

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{url}/chat/completions", headers=headers, json=payload)
        if resp.status_code != 200:
            print(f"LLM error {resp.status_code}: {resp.text[:500]}")
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]

# --- API Routes ---

async def index(request: Request):
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

async def _fetch_models():
    """Fetch available models from the LLM endpoint."""
    url = CONFIG.get("llm_url", "").rstrip("/")
    api_key = CONFIG.get("llm_api_key", "")
    try:
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{url}/models", headers=headers)
            resp.raise_for_status()
            return sorted(m["id"] for m in resp.json()["data"])
    except Exception:
        return []

async def api_config_get(request: Request):
    """Return config and available models."""
    models = await _fetch_models()
    return JSONResponse({
        "chat_model": CONFIG.get("chat_model"),
        "vision_model": CONFIG.get("vision_model"),
        "llm_url": CONFIG.get("llm_url", ""),
        "llm_api_key": CONFIG.get("llm_api_key", ""),
        "mcp_url": CONFIG.get("mcp_url", ""),
        "mcp_api_key": CONFIG.get("mcp_api_key", ""),
        "models": models,
    })

async def api_config_post(request: Request):
    """Update config, reinitialize MCP client, and save to config.json."""
    global mcp
    body = await request.json()

    # Update config with provided fields
    for key in ("llm_url", "llm_api_key", "mcp_url", "mcp_api_key", "chat_model", "vision_model"):
        if key in body:
            CONFIG[key] = body[key]

    # Reinitialize MCP client
    mcp = MCPClient(CONFIG["mcp_url"], CONFIG.get("mcp_api_key", ""))

    # Save to config.json
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    try:
        with open(config_path, "w") as f:
            json.dump(CONFIG, f, indent=2)
    except Exception as e:
        print(f"Warning: could not save config: {e}")

    # Fetch models from (possibly new) LLM endpoint
    models = await _fetch_models()
    return JSONResponse({
        "chat_model": CONFIG.get("chat_model"),
        "vision_model": CONFIG.get("vision_model"),
        "llm_url": CONFIG.get("llm_url", ""),
        "llm_api_key": CONFIG.get("llm_api_key", ""),
        "mcp_url": CONFIG.get("mcp_url", ""),
        "mcp_api_key": CONFIG.get("mcp_api_key", ""),
        "models": models,
    })

async def api_sensors(request: Request):
    """Get all sensor readings."""
    data = await mcp.call_tool("get_environment_sensors")
    return JSONResponse(data)

async def api_lights(request: Request):
    """Get all lights."""
    data = await mcp.call_tool("get_lights")
    return JSONResponse(data)

async def api_outlets(request: Request):
    """Get all outlets."""
    data = await mcp.call_tool("get_outlets")
    return JSONResponse(data)

async def api_command(request: Request):
    """Execute an MCP tool command."""
    body = await request.json()
    tool = body.get("tool")
    args = body.get("args", {})
    # Validate against tools actually available from MCP
    tools = await mcp.list_tools()
    known = {t["function"]["name"] for t in tools}
    if tool not in known:
        return JSONResponse({"error": f"Unknown tool: {tool}"}, status_code=400)
    result = await mcp.call_tool(tool, args)
    return JSONResponse({"result": result})

async def api_chat(request: Request):
    """Chat with the LLM. Handles tool calling loop automatically."""
    body = await request.json()
    user_message = body.get("message", "")
    history = body.get("history", [])
    model = body.get("model") or CONFIG.get("chat_model", "qwen3:4b")

    messages = [
        {"role": "system", "content": "You are a smart home assistant controlling IKEA Dirigera devices. "
         "Use your tools to list and control lights, outlets, and sensors. "
         "Always list devices first before trying to control them. Be concise."},
        *history,
        {"role": "user", "content": user_message},
    ]

    steps = []
    try:
        tools = await mcp.list_tools()
    except Exception as e:
        return JSONResponse({"steps": [{"type": "error", "content": f"MCP error: {e}"}]})

    def parse_content(content):
        """Extract <think> blocks and remaining text from LLM content."""
        if not content:
            return
        think_match = re.search(r"<think>([\s\S]*?)</think>", content)
        if think_match:
            thinking = think_match.group(1).strip()
            if thinking:
                steps.append({"type": "thinking", "content": thinking})
        text = re.sub(r"<think>[\s\S]*?</think>\s*", "", content).strip()
        if text:
            steps.append({"type": "text", "content": text})

    # Tool calling loop
    for _ in range(5):  # max 5 rounds
        try:
            result = await llm_chat(messages, tools=tools, model=model)
        except httpx.HTTPStatusError as e:
            try:
                err_detail = e.response.json().get("error", {}).get("message", str(e))
            except Exception:
                err_detail = str(e)
            steps.append({"type": "error", "content": f"LLM error: {err_detail}"})
            return JSONResponse({"steps": steps})
        except Exception as e:
            steps.append({"type": "error", "content": f"LLM error: {e}"})
            return JSONResponse({"steps": steps})

        if result.get("tool_calls"):
            # Show any text/thinking the model produced alongside tool calls
            parse_content(result.get("content", ""))
            messages.append(result)
            for tc in result["tool_calls"]:
                tool_name = tc["function"]["name"]
                raw_args = tc["function"].get("arguments", {})
                tool_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                try:
                    tool_result = await mcp.call_tool(tool_name, tool_args)
                    tool_result_str = json.dumps(tool_result)
                except Exception as e:
                    tool_result_str = json.dumps({"error": str(e)})
                steps.append({"type": "tool", "tool": tool_name, "args": tool_args, "result": tool_result_str})
                messages.append({"role": "tool", "content": tool_result_str,
                                 "tool_call_id": tc.get("id", tool_name)})
        else:
            parse_content(result.get("content", ""))
            return JSONResponse({"steps": steps})

    steps.append({"type": "error", "content": "Too many tool calls, giving up."})
    return JSONResponse({"steps": steps})

async def api_analyze(request: Request):
    """Analyze an image with a vision model."""
    body = await request.json()
    image_b64 = body.get("image", "")
    prompt = body.get("prompt", "Describe what you see in this image.")

    try:
        result = await llm_chat(
            [{"role": "user", "content": prompt}],
            images=[image_b64],
        )
        content = result.get("content", "")
        # Strip thinking tags from qwen3/gemma3
        import re
        cleaned = re.sub(r"<think>[\s\S]*?</think>\s*", "", content).strip()
        return JSONResponse({"response": cleaned or content})
    except Exception as e:
        return JSONResponse({"response": f"Vision analysis failed: {e}"}, status_code=500)

app = Starlette(routes=[
    Route("/", index),
    Route("/api/config", api_config_get),
    Route("/api/config", api_config_post, methods=["POST"]),
    Route("/api/sensors", api_sensors),
    Route("/api/lights", api_lights),
    Route("/api/outlets", api_outlets),
    Route("/api/command", api_command, methods=["POST"]),
    Route("/api/chat", api_chat, methods=["POST"]),
    Route("/api/analyze", api_analyze, methods=["POST"]),
])

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Load config and init MCP at module level so it works both with
# `python server.py` and `uvicorn server:app`
load_config()
mcp = MCPClient(CONFIG["mcp_url"], CONFIG["mcp_api_key"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full Agent Server")
    parser.add_argument("--port", type=int, default=9090, help="Port (default: 9090)")
    parser.add_argument("--host", default="127.0.0.1", help="Host")
    args = parser.parse_args()

    print(f"Full Agent Server on http://{args.host}:{args.port}")
    print(f"LLM: {CONFIG.get('llm_url')}")
    print(f"Dirigera MCP: {CONFIG['mcp_url']}")

    uvicorn.run(app, host=args.host, port=args.port)
