# Physical Agent Labs

> AI is moving from the digital world into the physical world.

Hands-on labs exploring how AI can control physical devices - robot arms, smart homes, and more.

## Prerequisites

Before the session, install:

### 1. Pixi (Package Manager)
```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

### 2. Ollama (Local LLM)
```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

Pull required models:
```bash
ollama pull qwen3:4b        # For agent labs (3, 5, 6)
ollama pull gemma3:4b       # For vision lab (4)
```

### 3. System Dependencies

**macOS:**
```bash
brew install portaudio  # For microphone access
```

**Linux:**
```bash
sudo apt install portaudio19-dev espeak
```

## Labs

| Lab | Topic | Description |
|-----|-------|-------------|
| [lab1_speech](lab1_speech/) | Speech | STT (whisper.cpp) + TTS (Piper) |
| [lab2_vision](lab2_vision/) | Vision | YOLO object detection & segmentation |
| [lab3_agent](lab3_agent/) | AI Agent | LLM with function calling (Ollama) |
| [lab4_business](lab4_business/) | Combined | Webcam + Vision LLM + Speech |
| [lab5_mcp](lab5_mcp/) | MCP | MCP server + Pydantic AI agent |
| [lab6_iot](lab6_iot/) | IoT | IKEA smart home via remote MCP |

## Quick Start

```bash
# Enter a lab
cd lab1_speech

# Install dependencies
pixi install

# Run demo
pixi run demo
```

## Hardware (Optional)

For the full experience with physical devices:
- **Candytron** - Niryo Ned 2 robot arm
- **IKEA Smart Home** - DIRIGERA hub + Zigbee devices
- **Reachy Mini** - Pollen Robotics humanoid

## Author

Joakim Eriksson, RISE Research Institutes of Sweden
