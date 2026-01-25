# Physical Agent Architecture Plan

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
