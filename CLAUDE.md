# Physical Agent Project

Project for Jfokus 2026 - 3.5 hour hands-on lab about AI controlling physical devices.

## Development Rules

- **Package manager:** Always use `pixi`, never pip directly
- **Lab structure:** Each lab has its own `pixi.toml` - self-contained
- **No external APIs:** Prefer local models (Whisper, Ollama, YOLO) over cloud APIs
- **Libraries:** Use existing libs like Pydantic AI, not custom protocol implementations

## Project Structure

```
physical-agent/
├── CLAUDE.md              # This file
├── labs/                  # Self-contained lab exercises
│   ├── lab1_speech/       # Speech: STT + TTS
│   │   ├── pixi.toml
│   │   └── main.py
│   ├── lab2_vision/       # Vision: YOLO object detection
│   │   └── pixi.toml
│   └── lab3_agent/        # AI agent with tools
│       └── pixi.toml
└── presentation/
    └── jfokus2026-slides/ # Slidev presentation (npm/node)
```

## Session: "AI in the Physical World"

AI is moving out from the digital world into the physical world. In this hands-on lab, participants explore how LLMs, multimodal AI, and edge intelligence can control real IoT devices and robotic systems.

### Hardware Setup

1. **Candytron 4000** (Niryo Ned 2)
   - 6-axis collaborative robot arm
   - External camera (YOLO for candy detection)
   - Microphone (speech input via Whisper)
   - Speaker (TTS output)
   - Table with candy
   - Code: Complete and working

2. **Reachy Mini** (Pollen Robotics)
   - Expressive robot head
   - Moves, looks around, interacts

3. **IKEA IoT Devices**
   - DIRIGERA hub + Zigbee devices
   - Smart lights, sensors, blinds

### Key Technologies

- LLMs with function calling / tool use
- MCP (Model Context Protocol)
- Computer Vision (YOLO 11)
- Speech pipeline (Whisper STT, TTS)
- Edge AI

### References

- MCP Agents: https://github.com/joakimeriksson/mcp-agents
- Candytron Demo: https://github.com/cluster1-arrowcolony/candytron-demo

## Development Commands

```bash
# Run a lab
cd labs/lab1_speech
pixi install
pixi run demo

# Run presentation (from presentation/jfokus2026-slides/)
npm run dev
```

## Author

Joakim Eriksson, RISE Research Institutes of Sweden
joakim.eriksson@ri.se
