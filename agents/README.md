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

## Candytron 4000 (`candytron/`)

Candy-dispensing robot with vision, speech, and robot arm control.

**Features:**
- Pick candy by color using robot arm (Niryo Ned 2)
- Detect candy on table using camera + YOLO
- Text-to-speech for friendly interaction
- Gesture controls (wave, dance)
- Virtual mode with canned responses for testing

**Usage:**

```bash
cd agents/candytron

# Virtual mode (no hardware)
pixi run agent

# With registry
REGISTRY_URL=http://localhost:8000 pixi run agent
```

**Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `REGISTRY_URL` | Agent registry URL | `http://localhost:8000` |
| `CANDYTRON_PORT` | Port for A2A server | `9999` |
| `CANDYTRON_URL` | Public URL for this agent | `http://localhost:9999` |
| `PYDANTIC_AI_MODEL` | LLM model to use | `ollama:gemma3:4b` |

**Real Hardware Integration:**

See `robot.py` for integration stubs. Uncomment and configure:
- `pyniryo` for Niryo Ned 2 robot arm
- `ultralytics` + `cv2` for camera and YOLO detection
- `piper-tts` for speech output
- `pywhispercpp` for voice commands

**Canned Image:**

Place a `candy_table.jpg` in the candytron directory to use as the canned camera response.

## Future Agents

- **Reachy Agent** - Robot head control
