# Production Agents

This folder contains production-ready A2A agents for the Jfokus lab stations.

## IoT Agent (`iot_agent/`)

Smart home control agent that connects to IKEA DIRIGERA via MCP.

**Features:**
- Controls lights (on/off, brightness, color)
- Reads environment sensors (temperature, humidity, CO2, VOC)
- Auto-registers with the agent registry
- Heartbeat to stay registered

**Usage:**

```bash
cd agents/iot_agent

# Set MCP server URL and run
DIRIGERA_MCP_URL=http://localhost:8080 pixi run agent

# With custom registry
DIRIGERA_MCP_URL=http://dirigera.local:8080 \
REGISTRY_URL=http://registry:8000 \
pixi run agent
```

**Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `DIRIGERA_MCP_URL` | URL of DIRIGERA MCP server | Required |
| `REGISTRY_URL` | Agent registry URL | `http://localhost:8000` |
| `IOT_AGENT_PORT` | Port for A2A server | `9998` |
| `IOT_AGENT_URL` | Public URL for this agent | `http://localhost:9998` |
| `PYDANTIC_AI_MODEL` | LLM model to use | `ollama:qwen3:4b` |

## Future Agents

- **Candytron Agent** - Robot arm control
- **Reachy Agent** - Robot head control
