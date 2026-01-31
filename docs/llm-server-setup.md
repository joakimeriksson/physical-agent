# LLM Server Setup for Jfokus 2026 Lab

This document describes the shared LLM server configuration for the hands-on lab.

## Remote Server

**IP:** `192.168.101.116`

### Ollama (Recommended for Agents)

- **URL:** `http://192.168.101.116:11434`
- **OpenAI-compatible:** `http://192.168.101.116:11434/v1`

**Available Models:**

| Model | Size | Tool Calling | Vision | Use Case |
|-------|------|--------------|--------|----------|
| qwen2.5:7b | 4.7 GB | ✅ Yes | ❌ No | Agents with tools |
| gemma3:latest | 3.3 GB | ❌ No | ✅ Yes | Vision/multimodal |

**Performance (warm):**

| Query Type | Time |
|------------|------|
| Simple (1 tool) | ~1.3s |
| Complex (3 tools) | ~2.5s |

### SGLang (Alternative)

- **URL:** `http://192.168.101.116:30000`
- **OpenAI-compatible:** `http://192.168.101.116:30000/v1`

**Available Models:**

| Model | Tool Calling | Notes |
|-------|--------------|-------|
| nvidia/Qwen3-8B-FP4 | ✅ Yes | Requires `--tool-call-parser qwen2` |
| nvidia/Llama-3.1-8B-Instruct-FP4 | ✅ Yes | Requires `--tool-call-parser llama3` |

**Note:** SGLang must be started with `--tool-call-parser` flag for tool calling to work.

## Configuration

### Environment Variables

Set these before running labs or agents:

```bash
# Point to remote Ollama server
export OLLAMA_BASE_URL=http://192.168.101.116:11434/v1

# Set default model for pydantic-ai agents
export PYDANTIC_AI_MODEL=ollama:qwen2.5:7b
```

### Per-Lab Configuration

| Lab | Model | Notes |
|-----|-------|-------|
| lab3_agent | qwen2.5:7b | Tool calling |
| lab4_business | gemma3:4b | Vision required (multimodal) |
| lab5_mcp | qwen2.5:7b | Tool calling via MCP |
| lab6_iot | qwen2.5:7b | IoT device control |
| lab7_voice | qwen2.5:7b | Voice + LLM |
| lab8_a2a | qwen2.5:7b | Agent-to-agent |
| lab9_voice_iot | qwen2.5:7b | Voice + IoT |

### Agent Configuration

All agents in `agents/` directory support environment variables:

```bash
# Candytron
OLLAMA_BASE_URL=http://192.168.101.116:11434/v1 \
PYDANTIC_AI_MODEL=ollama:qwen2.5:7b \
pixi run agent

# IoT Agent
OLLAMA_BASE_URL=http://192.168.101.116:11434/v1 \
PYDANTIC_AI_MODEL=ollama:qwen2.5:7b \
DIRIGERA_MCP_URL=http://localhost:8080 \
pixi run agent

# Reachy
OLLAMA_BASE_URL=http://192.168.101.116:11434/v1 \
PYDANTIC_AI_MODEL=ollama:qwen2.5:7b \
pixi run voice
```

## Tool Calling Comparison

### Ollama (qwen2.5:7b)

Proper OpenAI-compatible tool_calls format:

```json
{
  "choices": [{
    "message": {
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "set_light",
          "arguments": "{\"room\":\"kitchen\",\"on\":true}"
        }
      }]
    }
  }]
}
```

### SGLang (Qwen3 with parser)

Same format when started with `--tool-call-parser qwen2`:

```bash
python -m sglang.launch_server \
  --model nvidia/Qwen3-8B-FP4 \
  --tool-call-parser qwen2 \
  --host 0.0.0.0 \
  --port 30000
```

## Exposing Ollama to Network

If Ollama is only listening on localhost, configure it to listen on all interfaces:

### Snap Installation (Ubuntu)

```bash
sudo snap set ollama host=0.0.0.0
sudo snap set ollama origins="*"
sudo snap disable ollama
sudo pkill -9 ollama
sudo snap enable ollama
```

Verify:
```bash
ss -tlnp | grep 11434
# Should show: 0.0.0.0:11434
```

### Manual/Binary Installation

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

### Systemd Service

```bash
sudo systemctl edit ollama
```

Add:
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

## Troubleshooting

### Test Ollama Connection

```bash
curl http://192.168.101.116:11434/api/tags
```

### Test Tool Calling

```bash
curl -X POST "http://192.168.101.116:11434/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "Turn on the light"}],
    "tools": [{
      "type": "function",
      "function": {
        "name": "set_light",
        "parameters": {"type": "object", "properties": {"on": {"type": "boolean"}}}
      }
    }]
  }'
```

### Check Loaded Models

```bash
curl http://192.168.101.116:11434/api/ps
```

### Pull a Model

```bash
curl -X POST http://192.168.101.116:11434/api/pull \
  -d '{"name": "qwen2.5:7b"}'
```
