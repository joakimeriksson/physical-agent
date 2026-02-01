# Physical Agent Architecture Plan

## Session Progress (2026-01-29)

### Completed Today

#### Production IoT Agent (`agents/iot_agent/`)
- [x] Connects to real DIRIGERA hub via MCP (port 8081)
- [x] Device discovery at startup using MCP client
- [x] Dynamic system prompt with discovered device names
- [x] A2A skills with hierarchical naming convention:
  - `iot.light.control` - Light Control
  - `iot.sensor.environment` - Environment Sensors
  - `iot.outlet.control` - Outlet Control
- [x] 2-minute timeout for slow models (`ModelSettings(timeout=120)`)
- [x] Auto-registration with registry

#### Registry Improvements (`labs/lab10_registry/`)
- [x] Extended polling timeout to 90 seconds
- [x] Extended HTTP client timeout to 120 seconds
- [x] Fixed JSON escaping for agent card popup (HTML escape)
- [x] Skills now displayed in UI

#### Model Comparison Results
| Model | Size | Tool Calling | Speed | Recommendation |
|-------|------|--------------|-------|----------------|
| qwen3:4b | 2.5GB | Works | ~90s | Long `<think>` blocks |
| llama3.2:3b | 2GB | Broken | Fast | Outputs raw JSON |
| **qwen2.5:7b** | 4.7GB | **Works** | ~30s | **Recommended** |

### Running the Current System

```bash
# Terminal 1: DIRIGERA MCP Server
cd /path/to/mcp-agents/dirigera/fastmcp
uv run python dirigeramcp.py --transport sse --host 0.0.0.0 --port 8081

# Terminal 2: IoT Agent
cd agents/iot_agent
DIRIGERA_MCP_URL=http://localhost:8081 PYDANTIC_AI_MODEL=ollama:qwen2.5:7b pixi run agent

# Terminal 3: Registry
cd labs/lab10_registry
pixi run registry

# Access:
# - Registry UI: http://localhost:8000
# - IoT Agent: http://localhost:9998
```

---

## Planned Improvements

### Phase 1: SGLang for Performance (Priority: High)

Replace Ollama with SGLang for up to **5x faster** tool calling.

**Benefits:**
- RadixAttention for prefix caching (reuses system prompts)
- 3x faster JSON decoding (tool outputs)
- Speculative decoding, continuous batching

**Setup:**
```bash
pip install sglang

python -m sglang.launch_server \
    --model-path Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 --port 30000

# Use with IoT Agent (drop-in replacement)
OPENAI_BASE_URL=http://localhost:30000/v1 \
OPENAI_API_KEY=EMPTY \
PYDANTIC_AI_MODEL=openai:Qwen/Qwen2.5-7B-Instruct \
pixi run agent
```

**Reference:** https://github.com/sgl-project/sglang

---

### Phase 2: NVIDIA Jetson / Spark Edge Deployment (Priority: High)

Run the complete stack on NVIDIA edge hardware for standalone physical agents.

**Target Hardware:**
- NVIDIA Jetson Orin Nano (8GB) - Entry level
- NVIDIA Jetson AGX Orin (32-64GB) - Full performance
- NVIDIA Spark (upcoming edge AI platform)

**Edge Stack:**
```
┌─────────────────────────────────────────────────┐
│              NVIDIA Jetson / Spark              │
├─────────────────────────────────────────────────┤
│  SGLang + Qwen2.5-7B (quantized INT4/AWQ)      │
│  ───────────────────────────────────────────── │
│  IoT Agent (A2A server on port 9998)           │
│  ───────────────────────────────────────────── │
│  DIRIGERA MCP Server (port 8081)               │
│  ───────────────────────────────────────────── │
│  Whisper (speech) + YOLO (vision)              │
└─────────────────────────────────────────────────┘
           │
           ▼ (Network/Zigbee)
    IKEA DIRIGERA Hub
    └── Lights, Sensors, Outlets
```

**Tasks:**
- [ ] Test SGLang on Jetson Orin with CUDA
- [ ] Quantize Qwen2.5-7B to INT4/AWQ for memory efficiency
- [ ] Benchmark inference speed on Jetson vs laptop
- [ ] Create Docker/container for edge deployment
- [ ] Test with real DIRIGERA hub over network
- [ ] Add camera input for vision-based automation
- [ ] Wake word detection for hands-free control

**Quantization for Edge:**
```bash
# AWQ quantization (4-bit, recommended for Jetson)
python -m sglang.launch_server \
    --model-path Qwen/Qwen2.5-7B-Instruct-AWQ \
    --quantization awq

# Memory footprint
# FP16: ~14GB (too big for Orin Nano)
# INT4: ~4GB (fits on Orin Nano 8GB)
```

**Memory Requirements:**
| Model | FP16 | INT4/AWQ | Jetson Orin Nano 8GB |
|-------|------|----------|---------------------|
| Qwen2.5-7B | 14GB | 4GB | ✅ Fits |
| Qwen2.5-3B | 6GB | 2GB | ✅ Fits |
| Llama3.2-3B | 6GB | 2GB | ✅ Fits |

---

### Phase 2b: End-to-End Speech-to-Speech on Edge (Priority: High)

Test real-time voice interaction without cascade (STT→LLM→TTS).

**Candidate Models:**

| Model | Latency | Size | Edge Feasibility |
|-------|---------|------|------------------|
| **PersonaPlex** (NVIDIA) | 160-200ms | 7B | ✅ Ready in `experimental/` |
| **Moshi** (Kyutai) | 160-200ms | ~7B | ✅ Rust+CUDA, 4-bit quant |
| **Ultravox** (Fixie) | ~150ms TTFT | 8B | ⚠️ Needs optimization |
| **Mini-Omni** | ~300ms | ~7B | ⚠️ Quality issues |
| Cascade (Whisper+LLM+TTS) | 500-800ms | varies | ✅ Current approach |

#### PersonaPlex - Full-Duplex with Persona Control (READY TO TEST)

**Location:** `experimental/personaplex/` (already cloned and configured for M2 Mac)

[PersonaPlex](https://github.com/NVIDIA/personaplex) extends Moshi with **persona control**:

```bash
# Run on M2 Mac (already configured with CPU offload)
cd experimental/personaplex
pixi install
pixi run install-moshi
export HF_TOKEN=<your_huggingface_token>
pixi run server-ssl  # Web UI at https://localhost:8998
```

**Features:**
- Full-duplex (always listening, always generating)
- **Text-based role prompts** - define custom personas
- **Voice conditioning** - choose from 18 preset voices
- Handles interruptions and backchannels naturally
- Based on Moshi + Helium 7B backbone

**Voice Presets:**
```
Natural (conversational): NATF0-3 (female), NATM0-3 (male)
Variety (diverse):        VARF0-4 (female), VARM0-4 (male)
```

**Example Prompts for IoT Assistant:**
```
# General IoT assistant
You are a helpful smart home assistant. Control lights, read sensors, and
manage power outlets. Respond concisely and confirm actions taken.

# Specific persona
You work for SmartHome Labs and your name is Alex. You help users control
their IKEA DIRIGERA smart home devices including lights, sensors, and outlets.
Information: Available devices include Desk Lamp, Living Room Light, and
Environment Sensor. Always confirm what actions you've taken.
```

**Lab Opportunity:**
1. Run PersonaPlex server
2. Create custom "IoT Assistant" persona
3. Have real-time voice conversations about smart home control
4. Integrate with IoT Agent for actual device control

**Tasks:**
- [ ] Test PersonaPlex on M2 Mac with CPU offload
- [ ] Create IoT assistant persona prompt
- [ ] Benchmark latency on local hardware
- [ ] Test on NVIDIA Jetson with CUDA backend
- [ ] Integrate voice output with IoT agent for actual control

#### Moshi - Full-Duplex Speech LLM (Base Model)

[Moshi](https://github.com/kyutai-labs/moshi) is **always listening, always generating** - true full-duplex:

```bash
# Rust + CUDA backend (recommended for Jetson)
cd moshi/rust
cargo run --features cuda --bin moshi-backend -r -- standalone

# Python with quantization (4-bit for memory efficiency)
python -m moshi_mlx.local -q 4
```

**Features:**
- 160ms theoretical latency (200ms practical)
- Handles interruptions naturally
- Based on Helium 7B text LLM
- Uses Mimi neural audio codec

**Tasks:**
- [ ] Test Moshi Rust backend on Jetson Orin
- [ ] Benchmark latency and memory usage
- [ ] Integrate with IoT agent for voice control
- [ ] Test full-duplex conversation quality

#### Ultravox - Speech Understanding

[Ultravox](https://github.com/fixie-ai/ultravox) understands speech directly (no ASR):

```python
# 8B model for edge
from ultravox import Ultravox
model = Ultravox.from_pretrained("fixie-ai/ultravox-v0_4_1-llama-3_1-8b")
```

**Features:**
- Direct audio → LLM (no transcription step)
- ~150ms time-to-first-token
- Built on Llama 3.1 8B

**References:**
- [PersonaPlex GitHub](https://github.com/NVIDIA/personaplex) - NVIDIA's persona-controlled Moshi
- [PersonaPlex Weights](https://huggingface.co/nvidia/personaplex-7b-v1) - HuggingFace model
- [Moshi Paper](https://arxiv.org/abs/2410.00037)
- [Ultravox GitHub](https://github.com/fixie-ai/ultravox)
- [NVIDIA Jetson Edge LLM Guide](https://developer.nvidia.com/blog/getting-started-with-edge-ai-on-nvidia-jetson-llms-vlms-and-foundation-models-for-robotics/)

---

### Phase 3: Skill Standardization (Priority: Medium)

Since A2A has no global skill registry, define our convention:

```
iot.light.control        # On/off, brightness, color
iot.light.scene          # Scenes, schedules
iot.sensor.temperature   # Temperature readings
iot.sensor.humidity      # Humidity readings
iot.sensor.air_quality   # CO2, VOC, PM2.5
iot.outlet.control       # On/off
iot.outlet.energy        # Power monitoring
iot.blind.control        # Open/close, position
iot.climate.control      # HVAC, thermostats
```

**Discovery Tags:** `smart-home`, `ikea`, `dirigera`, `zigbee`, `lighting`, `sensors`

---

### Phase 4: Additional Agents (Priority: Medium)

- [ ] **Voice Agent** - Whisper STT + Piper TTS, A2A client
- [ ] **Vision Agent** - YOLO detection, occupancy sensing
- [ ] **Orchestrator Agent** - Multi-agent coordination

---

## Overview

Software architecture combining MCP (Model Context Protocol) and A2A (Agent-to-Agent Protocol) for the Jfokus 2026 hands-on lab. The architecture enables AI agents to control physical devices (Candytron, Reachy Mini, IKEA smart home) through a progressive, layered approach.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACES                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │  Speech UI   │    │   Web UI     │    │   CLI UI     │                  │
│   │ (Whisper/TTS)│    │  (Browser)   │    │  (Terminal)  │                  │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │
└──────────┼───────────────────┼───────────────────┼──────────────────────────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATOR LAYER                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    A2A Client / Coordinator                          │   │
│   │   - Discovers agents via Agent Cards                                 │   │
│   │   - Routes tasks to appropriate device agents                        │   │
│   │   - Coordinates multi-agent workflows                                │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  A2A AGENT:     │  │  A2A AGENT:     │  │  A2A AGENT:     │
│  Candytron      │  │  Reachy Mini    │  │  IKEA Home      │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ Agent Card:     │  │ Agent Card:     │  │ Agent Card:     │
│ - pick_candy    │  │ - wave          │  │ - set_light     │
│ - detect_candy  │  │ - point         │  │ - read_sensor   │
│ - speak         │  │ - look_at       │  │ - set_blinds    │
│ - listen        │  │ - express       │  │ - get_devices   │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ LLM (agnostic)  │  │ LLM (agnostic)  │  │ LLM (agnostic)  │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ MCP Tools       │  │ Direct API      │  │ MCP Tools       │
│ (optional)      │  │ (no MCP)        │  │ (dirigera MCP)  │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   HARDWARE      │  │   HARDWARE      │  │   HARDWARE      │
│ - Niryo Ned 2   │  │ - Reachy Mini   │  │ - DIRIGERA Hub  │
│ - Camera/YOLO   │  │ - Motors/Servos │  │ - Zigbee Devices│
│ - Mic/Speaker   │  │ - Camera        │  │ - Lights/Sensors│
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Framework Stack

| Layer | Framework | Why |
|-------|-----------|-----|
| **Agent Framework** | [PydanticAI](https://ai.pydantic.dev/) | Type-safe, "FastAPI for agents", native multi-provider support |
| **A2A Protocol** | PydanticAI `to_a2a()` | Built-in! One line to expose agent as A2A server |
| **LLM Providers** | PydanticAI native | Built-in support for OpenAI, Anthropic, Ollama, Gemini, etc. |
| **Local Models** | [Ollama](https://ollama.com/) | Run LLMs locally, `agent = Agent("ollama:llama3.2")` |
| **MCP Protocol** | [mcp](https://pypi.org/project/mcp/) | For Lab 1: exposing tools without agent logic |
| **HTTP Server** | Uvicorn | ASGI server for A2A endpoints |
| **Vision** | Ultralytics YOLO | Real-time object detection |
| **Speech** | Whisper + TTS | Speech-to-text and text-to-speech |

### PydanticAI Model Configuration

PydanticAI handles multi-provider LLM access natively:

```python
from pydantic_ai import Agent

# Cloud providers (simple string syntax)
agent = Agent("openai:gpt-4o")
agent = Agent("anthropic:claude-sonnet-4-20250514")
agent = Agent("google-gla:gemini-2.0-flash")

# Local via Ollama
agent = Agent("ollama:llama3.2")
agent = Agent("ollama:qwen2.5-coder:7b")

# Environment-based switching
import os
model = os.getenv("LLM_MODEL", "ollama:llama3.2")
agent = Agent(model)
```

No custom LLM wrapper needed - PydanticAI provides the abstraction layer.

## Core Components

### 1. MCP Server Framework (`libs/mcp/`)

Reusable MCP server components (building on existing mcp-agents patterns):

```python
# libs/mcp/server.py - Base MCP server with tool registration
# libs/mcp/tools.py - Common tool decorators and utilities

# Existing MCP servers to integrate:
# - candytron_mcp (from mcp-agents repo)
# - dirigera (from mcp-agents repo)
```

### 2. A2A Support (Built into PydanticAI)

PydanticAI has **native A2A support** - no wrapper needed:

```python
from pydantic_ai import Agent

# Create agent with tools
agent = Agent(
    "ollama:llama3.2",
    system_prompt="You control IKEA smart home devices..."
)

@agent.tool
async def set_light(device_id: str, brightness: int) -> str:
    """Control an IKEA smart light"""
    return f"Light {device_id} set to {brightness}%"

# Convert to A2A server with ONE LINE
app = agent.to_a2a()

# Run with: uvicorn agent:app --port 8001
```

The `to_a2a()` method automatically:
- Exposes the agent via A2A JSON-RPC protocol
- Handles conversation history and context
- Stores results as A2A artifacts
- Manages task lifecycle

### 3. Device Agents (`agents/`)

Each device is a PydanticAI agent that becomes an A2A server:

```python
# agents/ikea/agent.py
from pydantic_ai import Agent
import dirigera  # IKEA smart home SDK

agent = Agent(
    "ollama:llama3.2",
    system_prompt="You control IKEA smart home devices. Be helpful and concise.",
)

@agent.tool
async def set_light(device_id: str, brightness: int, color: str) -> str:
    """Control an IKEA smart light"""
    await dirigera.set_light(device_id, brightness, color)
    return f"Light {device_id} set to {color} at {brightness}%"

@agent.tool
async def read_sensor(sensor_id: str) -> dict:
    """Read temperature/humidity from IKEA sensor"""
    return await dirigera.read_sensor(sensor_id)

# Expose as A2A server
app = agent.to_a2a()

# Run: uvicorn agents.ikea.agent:app --port 8001
```

Agent structure:
```
agents/
├── candytron/
│   ├── agent.py          # PydanticAI agent → A2A server
│   └── tools.py          # pick_candy, detect_candy, speak
├── reachy/
│   ├── agent.py          # PydanticAI agent → A2A server
│   └── tools.py          # wave, point, look_at, express
└── ikea/
    ├── agent.py          # PydanticAI agent → A2A server
    └── tools.py          # set_light, read_sensor, set_blinds
```

### 5. Orchestrator (`orchestrator/`)

Coordinates multiple A2A agents:

```python
# orchestrator/coordinator.py
class AgentCoordinator:
    """Discovers and orchestrates multiple A2A agents"""

    async def discover_agents(self) -> list[AgentCard]: ...
    async def route_task(self, user_request: str) -> TaskResult: ...
    async def multi_agent_workflow(self, plan: list[Task]) -> list[TaskResult]: ...
```

## Project Structure

```
physical-agent/
├── CLAUDE.md
├── PLAN.md                        # This file
├── pyproject.toml                 # Python dependencies
├── libs/                          # Shared utilities (minimal)
│   └── mcp/                       # MCP server helpers (optional)
│       ├── __init__.py
│       └── server.py
├── agents/                        # Device agents (PydanticAI → A2A)
│   ├── candytron/
│   │   ├── __init__.py
│   │   ├── agent.py               # agent.to_a2a() server
│   │   └── tools.py               # pick_candy, detect_candy, speak
│   ├── reachy/
│   │   ├── __init__.py
│   │   ├── agent.py               # agent.to_a2a() server
│   │   └── tools.py               # wave, point, look_at
│   └── ikea/
│       ├── __init__.py
│       ├── agent.py               # agent.to_a2a() server
│       └── tools.py               # set_light, read_sensor
├── orchestrator/                  # Multi-agent coordination
│   └── coordinator.py             # A2A client calling device agents
├── labs/                          # Lab exercises
│   ├── lab1_mcp_basics/           # Simple MCP server
│   ├── lab2_pydantic_a2a/         # PydanticAI agent with to_a2a()
│   └── lab3_multi_agent/          # Multi-agent orchestration
├── examples/                      # Runnable demos
│   ├── simple_mcp_server.py
│   ├── single_a2a_agent.py
│   └── multi_agent_demo.py
├── presentation/                  # (existing)
└── docker-compose.yml             # Container deployment
```

## Lab Progression

### Lab 1: MCP Basics
**Goal:** Understand MCP tool exposure
- Create a simple MCP server with 2-3 tools
- Connect to it from Claude Desktop or custom client
- Control an IKEA light via MCP

### Lab 2: A2A Agent with Tools
**Goal:** Build an A2A-compliant agent
- Create Agent Card advertising capabilities
- Implement task handler with LLM reasoning
- Agent uses local tools (can include MCP tools)

### Lab 3: Multi-Agent Coordination
**Goal:** Multiple agents collaborating
- Deploy Candytron + IKEA agents
- Orchestrator discovers agents via Agent Cards
- Execute workflow: "Turn on lights, then give me candy"

## Key Dependencies

```toml
[project]
dependencies = [
    # Agent Framework (includes A2A support via to_a2a())
    "pydantic-ai[a2a]>=0.1",

    # MCP Protocol (for Lab 1)
    "mcp>=1.0",

    # Hardware/IoT
    "pyniryo>=1.1",           # Niryo Ned 2
    "reachy-sdk>=0.7",        # Reachy Mini
    "dirigera>=1.0",          # IKEA smart home

    # Vision/Audio
    "ultralytics>=8.0",       # YOLO 11
    "openai-whisper>=20230918",

    # Server
    "uvicorn>=0.29",
    "httpx>=0.27",            # A2A client requests
]

[project.optional-dependencies]
openai = ["openai>=1.0"]
anthropic = ["anthropic>=0.30"]
```

## Implementation Order

1. **agents/ikea/** - Simplest: PydanticAI + `to_a2a()` + dirigera
2. **agents/candytron/** - Complex: vision + speech + robot control
3. **agents/reachy/** - Humanoid robot tools
4. **orchestrator/** - A2A client coordinating multiple agents
5. **labs/** - Progressive exercises
6. **examples/** - Demo scripts

## Protocol Comparison

| Aspect | MCP | A2A |
|--------|-----|-----|
| Purpose | Agent-to-tool | Agent-to-agent |
| Communication | Tool calls | Task-based JSON-RPC |
| Discovery | Server config | Agent Cards |
| State | Stateless tools | Task lifecycle |
| Best for | Exposing capabilities | Multi-agent coordination |

## References

**Frameworks:**
- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [PydanticAI A2A Guide](https://ai.pydantic.dev/a2a/)
- [FastA2A (PydanticAI's A2A implementation)](https://github.com/pydantic/fasta2a)
- [Ollama](https://ollama.com/)

**Protocols:**
- [A2A Protocol Official Docs](https://a2a-protocol.org/latest/)
- [A2A GitHub Repository](https://github.com/a2aproject/A2A)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

**Project References:**
- [MCP Agents (existing code)](https://github.com/joakimeriksson/mcp-agents)
