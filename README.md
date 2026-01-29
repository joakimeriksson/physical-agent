# AI in Control of Things

**Building Physical AI Agents with IoT, Robots, and LLMs**

Jfokus 2026 - Hands-on Lab (3.5 hours)

> **Note:** This tutorial is under active development and being improved continuously. If you encounter issues or have suggestions, please open an issue or pull request.

AI is breaking out of the chat window and into the real world. In this session, you'll build AI agents that don't just talk—they see, listen, and physically act. We'll connect LLMs to a robotic arm (the "Candytron 4000"), cameras, microphones, and smart home devices, creating an interactive system where your voice commands and AI decisions translate into real-world actions. You'll explore multimodal AI, edge computing, and agent-to-agent communication—all running locally, no cloud required.

And yes, the robot will be handing out candy!

## What You'll Build

- **Speech pipelines** - Voice input (Whisper) and text-to-speech output
- **Computer vision** - Object detection with YOLO
- **AI agents with tools** - LLMs that take actions via function calling
- **Agent-to-agent communication** - The A2A protocol
- **IoT control** - Smart lights and devices via AI
- **Robots!** - Hands-on time with Candytron 4000 and Reachy Mini

## Prerequisites

### Required

1. **Pixi** (Python package manager)

   macOS/Linux:
   ```bash
   curl -fsSL https://pixi.sh/install.sh | bash
   ```
   Windows (PowerShell):
   ```powershell
   iwr -useb https://pixi.sh/install.ps1 | iex
   ```

2. **Ollama** (local LLM runtime)

   Download for your platform: https://ollama.com/download

   After installing, pull a model:
   ```bash
   ollama pull qwen3:4b
   ```

3. **Git** - clone this repository:
   ```bash
   git clone https://github.com/joakimeriksson/physical-agent.git
   ```

4. **A code editor** (VS Code recommended)

### Optional but Recommended

- A webcam and microphone on your laptop (for speech and vision labs)

No cloud API keys needed - we run everything locally!

## Getting Started

Each lab is self-contained with its own dependencies:

```bash
cd labs/lab1_speech
pixi install
pixi run demo
```

## Session Structure

### Part 1: Foundation Labs (~2 hours)

Everyone works through progressive exercises on their laptops:

| Lab | Topic | Description |
|-----|-------|-------------|
| 1 | Speech | Whisper STT + Piper TTS |
| 2 | Vision | YOLO 11 object detection |
| 3 | Agent | Pydantic AI + Ollama function calling |
| 4 | Business | Vision + Speech + VLM combined |
| 5 | MCP | MCP server pattern |
| 6 | IoT | Remote MCP to IKEA DIRIGERA |
| 7 | Voice | Voice pipeline integration |
| 8 | A2A | Agent-to-agent communication |
| 9 | Voice IoT | Voice-controlled IoT agent |
| 10 | Registry | A2A agent discovery and registry |

### Part 2: Station Rotation (~1.5 hours)

Groups rotate through 3 physical device stations:

- **Candytron 4000** - Niryo Ned 2 robot arm with vision and speech
- **Reachy Mini** - Expressive robot head
- **IKEA Smart Home** - DIRIGERA hub with lights, sensors, and blinds

## Project Structure

```
physical-agent/
├── labs/
│   ├── lab1_speech/       # Speech: STT + TTS
│   ├── lab2_vision/       # Vision: YOLO object detection
│   ├── lab3_agent/        # AI agent with tools
│   ├── lab4_business/     # Multi-modal business coach
│   ├── lab5_mcp/          # MCP server pattern
│   ├── lab6_iot/          # IoT control via MCP
│   ├── lab7_voice/        # Voice pipeline
│   ├── lab8_a2a/          # Agent-to-agent (A2A)
│   ├── lab9_voice_iot/    # Voice-controlled IoT
│   └── lab10_registry/    # A2A agent registry
└── presentation/
    └── jfokus2026-slides/ # Slidev presentation
```

## Standards and Documentation

### A2A (Agent-to-Agent Protocol)
- [A2A Protocol Specification](https://google.github.io/A2A/)
- [A2A GitHub Repository](https://github.com/google/A2A)
- [a2a-sdk Python Package](https://pypi.org/project/a2a-sdk/)

### MCP (Model Context Protocol)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### Pydantic AI
- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [Pydantic AI GitHub](https://github.com/pydantic/pydantic-ai)

### Computer Vision & Speech
- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Piper TTS](https://github.com/rhasspy/piper)

### Local LLM
- [Ollama](https://ollama.com/)

## Author

**Joakim Eriksson**
RISE Research Institutes of Sweden
joakim.eriksson@ri.se

## References

- [MCP Agents](https://github.com/joakimeriksson/mcp-agents)
- [Candytron Demo](https://github.com/cluster1-arrowcolony/candytron-demo)
