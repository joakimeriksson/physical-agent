# AI in the Physical World

**Jfokus 2026 - Hands-on Lab (3.5 hours)**

AI is moving out from the digital world into the physical world. In this hands-on lab, participants explore how LLMs, multimodal AI, and edge intelligence can control real IoT devices and robotic systems.

## What You'll Learn

- Connect LLMs to real physical devices
- Add computer vision so AI can see (YOLO 11)
- Add speech so AI can hear and talk (Whisper, Piper)
- Make AI take action in the real world
- Use MCP (Model Context Protocol) for tool integration

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

### Part 2: Station Rotation (~1.5 hours)

Groups rotate through 3 physical device stations:

- **Candytron 4000** - Niryo Ned 2 robot arm with vision and speech
- **Reachy Mini** - Expressive robot head
- **IKEA Smart Home** - DIRIGERA hub with lights, sensors, and blinds

## Getting Started

Each lab is self-contained with its own dependencies:

```bash
cd labs/lab1_speech
pixi install
pixi run demo
```

## Project Structure

```
physical-agent/
├── labs/
│   ├── lab1_speech/      # Speech: STT + TTS
│   ├── lab2_vision/      # Vision: YOLO object detection
│   ├── lab3_agent/       # AI agent with tools
│   ├── lab4_business/    # Multi-modal business coach
│   ├── lab5_mcp/         # MCP server pattern
│   └── lab6_iot/         # IoT control via MCP
└── presentation/
    └── jfokus2026-slides/ # Slidev presentation
```

## Requirements

- Python 3.12+
- [Pixi](https://pixi.sh) package manager
- Webcam (for vision labs)
- Microphone (for speech labs)
- [Ollama](https://ollama.ai) with qwen3:4b model

## Author

**Joakim Eriksson**
RISE Research Institutes of Sweden
joakim.eriksson@ri.se

## References

- [MCP Agents](https://github.com/joakimeriksson/mcp-agents)
- [Candytron Demo](https://github.com/cluster1-arrowcolony/candytron-demo)
