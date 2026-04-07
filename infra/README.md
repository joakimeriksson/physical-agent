# Infrastructure Setup

Server-side setup for the hackathon. Runs on the shared server (NVIDIA Jetson AGX Orin 64GB).

## Components

| Service | Port | Tunnel hostname | Auth |
|---------|------|-----------------|------|
| Dirigera MCP | 8000 | dirigera.botbox.se | API key → JWT → Bearer |
| Ollama proxy | 11435 | ollama.botbox.se | Bearer token |
| Ollama (raw) | 11434 | (not exposed) | None |
| Cloudflared | — | — | — |

## 1. Ollama

```bash
# Start Ollama with performance settings for 40 users
OLLAMA_NUM_PARALLEL=4 \
OLLAMA_MAX_LOADED_MODELS=3 \
OLLAMA_KEEP_ALIVE=60m \
OLLAMA_ORIGINS="*" \
ollama serve
```

Pre-load models:
```bash
ollama pull qwen3:4b      # Text/tool calling (2.5 GB)
ollama pull gemma3:4b      # Vision (3.3 GB)
ollama pull qwen3:14b      # Bigger model for challenges (9.3 GB)
```

## 2. Ollama Auth Proxy

```bash
cd infra
pip install starlette uvicorn httpx
python ollama_proxy.py --api-key YOUR_SHARED_KEY --host 127.0.0.1 --port 11435
```

## 3. Dirigera MCP Server

```bash
cd /path/to/mcp-agents/dirigera/fastmcp
uv run dirigeramcp.py --transport streamable-http --auth --host 127.0.0.1 --port 8000
```

On first run with `--auth`, it generates an API key and saves it to `config.toml`.

## 4. Cloudflare Tunnel

```bash
# One-time setup
cloudflared tunnel login
cloudflared tunnel create hackathon
cloudflared tunnel route dns hackathon dirigera.botbox.se
cloudflared tunnel route dns hackathon ollama.botbox.se

# Copy config
cp cloudflared-config.yml ~/.cloudflared/config.yml
# Edit: add tunnel ID and credentials path

# Run
cloudflared tunnel run hackathon
```

## Participant Info (show on projector)

```
Ollama URL:    https://ollama.botbox.se
Ollama API key: <your-key>

Dirigera URL:  https://dirigera.botbox.se
Dirigera API key: <your-key>

Repo: git clone https://github.com/joakimeriksson/physical-agent.git
Labs: open browser-labs/ in your browser
```
