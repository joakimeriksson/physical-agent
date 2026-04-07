# Infrastructure Setup

Server-side setup for the hackathon. Runs on the shared server (NVIDIA Spark 128GB).

## Components

| Service | Port | Tunnel hostname | Auth |
|---------|------|-----------------|------|
| Dirigera MCP | 8000 | dirigera.botbox.se | API key → JWT → Bearer |
| Ollama proxy | 11435 | ollama.botbox.se | Bearer token |
| Ollama (raw) | 11434 | (not exposed) | None |
| Cloudflared | — | — | — |

## Quick Start (4 terminals)

### Terminal 1: Ollama

```bash
OLLAMA_NUM_PARALLEL=4 \
OLLAMA_MAX_LOADED_MODELS=3 \
OLLAMA_KEEP_ALIVE=60m \
OLLAMA_ORIGINS="*" \
ollama serve
```

Pre-load models (run once, in a separate shell):
```bash
ollama pull qwen3:4b        # Text/tool calling (2.5 GB)
ollama pull gemma3:latest    # Vision (3.3 GB)
ollama pull qwen3:14b        # Bigger model for challenges (9.3 GB)
```

### Terminal 2: Ollama Auth Proxy

```bash
cd infra
pixi install
pixi run python ollama_proxy.py --api-key YOUR_SHARED_KEY --host 127.0.0.1 --port 11435
```

### Terminal 3: Dirigera MCP Server

```bash
cd /path/to/mcp-agents/dirigera/fastmcp
uv run dirigeramcp.py --transport streamable-http --auth --host 127.0.0.1 --port 8000
```

On first run with `--auth`, it auto-generates an API key and JWT secret, saved to `config.toml`.
The API key is printed on startup. Subsequent runs reuse the same key.

### Terminal 4: Cloudflare Tunnel

```bash
/tmp/cloudflared tunnel run dirigera-mcp
```

## One-Time Setup (already done)

### Cloudflared binary (arm64)

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 \
  -o /tmp/cloudflared && chmod +x /tmp/cloudflared
```

### Tunnel creation

```bash
/tmp/cloudflared tunnel login
/tmp/cloudflared tunnel create dirigera-mcp
/tmp/cloudflared tunnel route dns dirigera-mcp dirigera.botbox.se
/tmp/cloudflared tunnel route dns dirigera-mcp ollama.botbox.se
```

### Tunnel config (`~/.cloudflared/config.yml`)

```yaml
tunnel: <tunnel-id>
credentials-file: /home/<user>/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: dirigera.botbox.se
    service: http://localhost:8000
  - hostname: ollama.botbox.se
    service: http://localhost:11435
  - service: http_status:404
```

## Verification

After all 4 services are running:

```bash
# Test Ollama proxy (should return model list)
curl -s https://ollama.botbox.se/api/tags -H "Authorization: Bearer YOUR_SHARED_KEY"

# Test without auth (should return 401)
curl -s https://ollama.botbox.se/api/tags

# Test Dirigera auth (should return JWT token)
curl -s https://dirigera.botbox.se/auth/token \
  -X POST -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_MCP_KEY"}'

# Test Dirigera MCP (get sensor data)
TOKEN=$(curl -s https://dirigera.botbox.se/auth/token \
  -X POST -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_MCP_KEY"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

curl -s https://dirigera.botbox.se/mcp -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

## Participant Info (show on projector)

```
=== Hackathon Setup ===

1. Clone the repo:
   git clone https://github.com/joakimeriksson/physical-agent.git

2. Configure:
   cd physical-agent/browser-labs
   cp config.example.json config.json
   # Edit config.json with the keys below

3. Run lab4 (main lab):
   cd lab4_full_agent
   pixi install
   pixi run server
   # Open http://localhost:8080

=== Connection Info ===

Ollama URL:        https://ollama.botbox.se
Ollama API key:    <show-key>

Dirigera MCP URL:  https://dirigera.botbox.se
Dirigera API key:  <show-key>

Models available:  qwen3:4b, qwen3:14b, gemma3:latest
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Port already in use | `lsof -ti:PORT \| xargs kill` |
| Ollama 404 on model | `ollama pull MODEL_NAME` |
| CORS errors in browser | Make sure MCP server has CORSMiddleware (already added) |
| Tunnel not connecting | Check `~/.cloudflared/config.yml` has correct tunnel ID |
| MCP "Session not found" | Session expired, refresh the page |
| Slow responses | 40 users queuing — `OLLAMA_NUM_PARALLEL=4` helps |
