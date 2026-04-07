#!/usr/bin/env python3
"""Full Agent Server - bridges browser UI to Ollama and Dirigera MCP.

The browser handles camera, microphone, and UI.
This server handles LLM calls and IoT device control.

Usage:
    pixi run server
    pixi run server --port 8080
"""

import argparse
import json
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
            "ollama_url": "https://ollama.botbox.se",
            "ollama_api_key": "",
            "mcp_url": "https://dirigera.botbox.se",
            "mcp_api_key": "",
            "chat_model": "qwen3:4b",
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

    async def call_tool(self, tool_name, arguments=None):
        """Call an MCP tool. Returns the parsed result."""
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
                    "jsonrpc": "2.0", "id": self.call_id, "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments or {}}
                })

        # Handle session expiry
        if resp.status_code in (404, 400):
            self.session_id = None
            return await self.call_tool(tool_name, arguments)

        # Parse SSE response
        text = resp.text
        for line in text.split("\n"):
            if line.startswith("data: "):
                data = json.loads(line[6:])
                if "result" in data:
                    result = data["result"]
                    if "structuredContent" in result:
                        return result["structuredContent"]["result"]
                    if "content" in result:
                        return json.loads(result["content"][0]["text"])
                if "error" in data:
                    raise Exception(data["error"]["message"])
        raise Exception("Unexpected MCP response")

mcp = None

# --- Ollama Client ---

async def ollama_chat(messages, tools=None, model=None, images=None):
    """Chat with Ollama. Returns the response message."""
    url = CONFIG.get("ollama_url", "").rstrip("/")
    api_key = CONFIG.get("ollama_api_key", "")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model or CONFIG.get("chat_model", "qwen3:4b"),
        "messages": messages,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools
    if images:
        # Use /api/chat with multimodal messages for vision
        payload["model"] = model or CONFIG.get("vision_model", "gemma3:latest")
        payload.pop("tools", None)
        # Add images to the last user message
        for msg in reversed(payload["messages"]):
            if msg["role"] == "user":
                msg["images"] = images
                break

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{url}/api/chat", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json().get("message", {})

# --- IoT Tool definitions for Ollama ---

IOT_TOOLS = [
    {"type": "function", "function": {"name": "get_lights", "description": "List all smart lights with status.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_environment_sensors", "description": "List all sensors with temperature, humidity, CO2, PM2.5.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_outlets", "description": "List all power outlets.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "set_onoff", "description": "Turn a device on or off by name.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "is_on": {"type": "boolean"}}, "required": ["name", "is_on"]}}},
    {"type": "function", "function": {"name": "set_light_level", "description": "Set brightness 0-100.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "light_level": {"type": "integer"}}, "required": ["name", "light_level"]}}},
    {"type": "function", "function": {"name": "set_light_color", "description": "Set light color.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "color_hue": {"type": "number", "description": "0-360"}, "color_saturation": {"type": "number", "description": "0.0-1.0"}}, "required": ["name", "color_hue", "color_saturation"]}}},
]

# --- API Routes ---

async def index(request: Request):
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

async def api_config(request: Request):
    """Return config and available models from Ollama."""
    models = []
    try:
        url = CONFIG.get("ollama_url", "").rstrip("/")
        headers = {}
        if CONFIG.get("ollama_api_key"):
            headers["Authorization"] = f"Bearer {CONFIG['ollama_api_key']}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{url}/api/tags", headers=headers)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        pass
    return JSONResponse({
        "chat_model": CONFIG.get("chat_model"),
        "vision_model": CONFIG.get("vision_model"),
        "ollama_url": CONFIG.get("ollama_url"),
        "mcp_url": CONFIG.get("mcp_url"),
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
    """Execute an IoT command."""
    body = await request.json()
    tool = body.get("tool")
    args = body.get("args", {})
    if tool not in ("set_onoff", "set_light_level", "set_light_color"):
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

    tool_calls_log = []

    # Tool calling loop
    for _ in range(5):  # max 5 rounds
        result = await ollama_chat(messages, tools=IOT_TOOLS, model=model)

        if result.get("tool_calls"):
            messages.append(result)
            for tc in result["tool_calls"]:
                tool_name = tc["function"]["name"]
                tool_args = tc["function"].get("arguments", {})
                try:
                    tool_result = await mcp.call_tool(tool_name, tool_args)
                    tool_result_str = json.dumps(tool_result)
                except Exception as e:
                    tool_result_str = json.dumps({"error": str(e)})
                tool_calls_log.append({"tool": tool_name, "args": tool_args, "result": tool_result_str})
                messages.append({"role": "tool", "content": tool_result_str})
        else:
            # Final text response
            content = result.get("content", "")
            # Strip thinking tags from qwen3
            import re
            cleaned = re.sub(r"<think>[\s\S]*?</think>\s*", "", content).strip()
            return JSONResponse({
                "response": cleaned or content,
                "tool_calls": tool_calls_log,
            })

    return JSONResponse({"response": "Too many tool calls, giving up.", "tool_calls": tool_calls_log})

async def api_analyze(request: Request):
    """Analyze an image with a vision model."""
    body = await request.json()
    image_b64 = body.get("image", "")
    prompt = body.get("prompt", "Describe what you see in this image.")

    try:
        result = await ollama_chat(
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
    Route("/api/config", api_config),
    Route("/api/sensors", api_sensors),
    Route("/api/lights", api_lights),
    Route("/api/outlets", api_outlets),
    Route("/api/command", api_command, methods=["POST"]),
    Route("/api/chat", api_chat, methods=["POST"]),
    Route("/api/analyze", api_analyze, methods=["POST"]),
])

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full Agent Server")
    parser.add_argument("--port", type=int, default=8080, help="Port (default: 8080)")
    parser.add_argument("--host", default="127.0.0.1", help="Host")
    args = parser.parse_args()

    load_config()
    mcp = MCPClient(CONFIG["mcp_url"], CONFIG["mcp_api_key"])

    print(f"Full Agent Server on http://{args.host}:{args.port}")
    print(f"Ollama: {CONFIG['ollama_url']}")
    print(f"Dirigera MCP: {CONFIG['mcp_url']}")

    uvicorn.run(app, host=args.host, port=args.port)
