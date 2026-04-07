#!/usr/bin/env python3
"""Simple auth proxy for Ollama. Checks Bearer token, proxies to Ollama.

Usage:
    python ollama_proxy.py --api-key YOUR_KEY
    python ollama_proxy.py --api-key YOUR_KEY --port 11435 --ollama-url http://localhost:11434
"""

import argparse
import httpx
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route
import uvicorn

API_KEY = None
OLLAMA_URL = None


async def check_auth(request: Request):
    """Return None if auth is valid, or a JSONResponse error."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JSONResponse({"error": "Missing Bearer token"}, status_code=401)
    if auth[7:] != API_KEY:
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    return None


async def proxy(request: Request):
    """Proxy any request to Ollama after auth check."""
    error = await check_auth(request)
    if error:
        return error

    path = request.url.path
    query = str(request.url.query)
    target = f"{OLLAMA_URL}{path}"
    if query:
        target += f"?{query}"

    body = await request.body()
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "authorization")}

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        resp = await client.request(
            method=request.method,
            url=target,
            content=body,
            headers=headers,
        )

    return StreamingResponse(
        content=iter([resp.content]),
        status_code=resp.status_code,
        headers={k: v for k, v in resp.headers.items()
                 if k.lower() not in ("content-encoding", "transfer-encoding")},
    )


app = Starlette(routes=[
    Route("/{path:path}", proxy, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]),
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ollama auth proxy")
    parser.add_argument("--api-key", required=True, help="Bearer token to require")
    parser.add_argument("--port", type=int, default=11435, help="Port to listen on (default: 11435)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama backend URL")
    args = parser.parse_args()

    API_KEY = args.api_key
    OLLAMA_URL = args.ollama_url.rstrip("/")

    print(f"Ollama proxy listening on {args.host}:{args.port}")
    print(f"Proxying to {OLLAMA_URL}")
    print(f"API key: {API_KEY}")

    uvicorn.run(app, host=args.host, port=args.port)
