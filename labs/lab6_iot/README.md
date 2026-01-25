# Lab 6: IoT Control

> **Physical Agent Lab Series**
> AI is moving from the digital world into the physical world. This lab connects to real IKEA smart home devices via a remote MCP server.

Control IKEA smart home devices (lights, outlets, sensors) through natural language.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Lab Network                              │
│                                                                 │
│  ┌─────────────────┐              ┌─────────────────────────┐   │
│  │  Your Laptop    │              │    IoT Server           │   │
│  │                 │    HTTP      │                         │   │
│  │  lab6_iot       │◄────────────►│  dirigeramcp.py         │   │
│  │  agent.py       │   (MCP)      │  --transport            │   │
│  │                 │              │    streamable-http      │   │
│  └────────┬────────┘              └───────────┬─────────────┘   │
│           │                                   │                 │
│           ▼                                   ▼                 │
│  ┌─────────────────┐              ┌─────────────────────────┐   │
│  │     Ollama      │              │    IKEA DIRIGERA Hub    │   │
│  │  (qwen3:4b)  │              │    ┌─────────────────┐  │   │
│  └─────────────────┘              │    │ Lights          │  │   │
│                                   │    │ Outlets         │  │   │
│                                   │    │ Sensors         │  │   │
│                                   │    └─────────────────┘  │   │
│                                   └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

```bash
ollama pull qwen3:4b
```

## Setup

```bash
pixi install
```

## Usage

```bash
# Connect to MCP server (ask instructor for IP)
pixi run agent --server http://<server-ip>:8000/mcp

# Or if running locally
pixi run agent
```

## Available Commands

| Command | Description |
|---------|-------------|
| "What lights are available?" | List all lights |
| "Turn on the kitchen light" | Control specific light |
| "Set bedroom light to 50%" | Adjust brightness |
| "What's the temperature?" | Read sensors |
| "Turn off all lights" | Bulk control |

## Example Session

```
Connecting to MCP server: http://192.168.1.100:8000/mcp
Available IoT tools: ['get_lights', 'get_outlets', 'get_environment_sensors',
                      'set_onoff', 'set_light_level', 'set_light_color']

IoT Agent ready! Using qwen3:4b
Type 'quit' to exit.

You: What lights do we have?
Agent: I found 3 lights:
- Kitchen Light (on, 80% brightness)
- Living Room (off)
- Bedroom Lamp (on, 40% brightness)

You: Turn off the kitchen light
Agent: Done! Kitchen Light is now off.

You: What's the temperature in the kitchen?
Agent: The kitchen sensor shows:
- Temperature: 22.5°C
- Humidity: 45%
- Air quality (VOC): 150

You: quit
Goodbye!
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `get_lights` | List all lights with status |
| `get_outlets` | List outlets with power usage |
| `get_environment_sensors` | Temperature, humidity, PM2.5, VOC |
| `set_onoff` | Turn device on/off |
| `set_light_level` | Set brightness 0-100 |
| `set_light_color` | Set hue and saturation |

## Running the Server

The instructor runs the MCP server:
```bash
cd /path/to/mcp-agents/dirigera/fastmcp
uv run dirigeramcp.py --transport streamable-http --host 0.0.0.0 --port 8000
```
