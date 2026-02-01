---
theme: default
title: AI in Control of Things
info: |
  ## AI in Control of Things
  Building Physical AI Agents with IoT, Robots, and LLMs

  Hands-on lab at Jfokus 2026
author: Joakim Eriksson
keywords: AI, LLM, Robotics, IoT, Edge AI, A2A, MCP
highlighter: shiki
drawings:
  persist: false
transition: slide-left
mdc: true
---

# AI in Control of Things

## Building Physical AI Agents with IoT, Robots, and LLMs

<div class="pt-12">
  <span class="px-2 py-1 rounded">
    Jfokus 2026 - Hands-on Lab (3.5 hours)
  </span>
</div>

<div class="abs-br m-6 flex gap-2">
  <span class="text-sm opacity-50">Joakim Eriksson, RISE</span>
</div>

---

# What We'll Do Today

<v-clicks>

- 🤖 Connect LLMs to **real physical devices**
- 👁️ Add **computer vision** so AI can see
- 🎤 Add **speech** so AI can hear and talk
- 🔗 Make agents **talk to each other** (A2A)
- 🦾 Make AI **take action** in the real world
- 🍬 Get candy from a robot!

</v-clicks>

---
layout: two-cols
---

# The Shift

AI is moving from the **digital** world...

<v-click>

- Chatbots
- Text generation
- Image creation
- Code completion

</v-click>

::right::

<v-click>

# Into the Physical

...into the **physical** world

- Autonomous vehicles
- Smart factories
- Home robots
- Connected products

</v-click>

---
layout: center
class: text-center
---

# Our Hardware Today

Three ways to interact with the physical world

---
layout: two-cols
---

# Candytron 4000

### Niryo Ned 2
- 6-axis collaborative robot arm
- Gripper for manipulation
- Camera for vision
- Microphone for speech
- Speaker for responses
- Table full of candy!

::right::

<div class="pl-4 pt-12">

```
     Mic       Camera
        \      /
         \    /
      +----------+
      |   Ned 2  |
      +----+-----+
           |
    +------+------+
    |  Candy Table |
    +-------------+
```

</div>

---
layout: two-cols
---

# Reachy Mini

### Pollen Robotics
- Expressive robot head
- Antennas for expression
- Camera in head
- Moves and looks around
- Natural interaction

::right::

<div class="flex items-center justify-center h-full text-9xl">

🤖

</div>

---
layout: two-cols
---

# IKEA Smart Home

### DIRIGERA Hub + Devices
- Smart lights (color, brightness)
- Motion sensors
- Temperature sensors
- Blinds control
- All via Zigbee

Your AI can control the environment!

::right::

<div class="pl-4 pt-12">

```
      Lights
        |
    +---+---+
    |DIRIGERA|---- Sensors
    +---+---+
        |
      Blinds
```

</div>

---
layout: center
---

# Key Technologies

The building blocks for physical AI

---

# Two Protocols for AI Integration

<div class="grid grid-cols-2 gap-8 pt-4">

<div>

### MCP (Model Context Protocol)

**Client-Server pattern**

```
┌─────────┐      ┌─────────┐
│   LLM   │ ───► │   MCP   │
│ (Client)│      │ (Server)│
└─────────┘      └─────────┘
```

- LLM discovers and uses tools
- Structured tool definitions
- Resources and prompts
- **modelcontextprotocol.io**

</div>

<div>

### A2A (Agent-to-Agent)

**Peer-to-peer pattern**

```
┌─────────┐      ┌─────────┐
│ Agent A │ ◄──► │ Agent B │
│         │      │         │
└─────────┘      └─────────┘
```

- Agents discover each other
- Exchange messages (tasks)
- Agent Cards for identity
- **google.github.io/A2A**

</div>

</div>

---

# The Brain: LLM with Tools

```python
from pydantic_ai import Agent

agent = Agent("ollama:qwen3:4b")

@agent.tool
def pick_candy(color: str) -> str:
    """Pick up a candy of the specified color from the table"""
    position = vision.find_candy(color)
    robot.move_to(position)
    robot.grip()
    robot.move_to(HANDOVER_POSITION)
    return f"Picked up {color} candy"

# LLM decides WHEN and HOW to use tools
result = agent.run_sync("Can I have a red candy?")
```

---

# The Eyes: Computer Vision

```python
from ultralytics import YOLO
model = YOLO("candy-detector.pt")

def find_candy(color: str) -> Position:
    """Detect candies and find one matching the color"""
    frame = camera.capture()
    results = model(frame)

    for detection in results:
        if detection.label == "candy" and detection.color == color:
            return detection.position

    return None
```

YOLO 11 for real-time object detection

---

# Ears & Mouth: Speech Pipeline

```python
# Speech-to-Text (Ears)
audio = microphone.listen()
text = whisper.transcribe(audio)

# Text-to-Speech (Mouth)
response = llm.generate(text)
speaker.play(tts.synthesize(response))
```

<v-click>

The complete loop:
1. **Hear** → "Can I have a red candy?"
2. **Think** → LLM decides to call `pick_candy("red")`
3. **See** → Camera finds red candy position
4. **Act** → Robot picks and delivers
5. **Speak** → "Here's your red candy!"

</v-click>

---
layout: center
---

# Prerequisites

What you need installed

---

# Setup Checklist

<v-clicks>

### 1. Pixi (Python package manager)
```bash
# macOS/Linux
curl -fsSL https://pixi.sh/install.sh | bash

# Windows PowerShell
iwr -useb https://pixi.sh/install.ps1 | iex
```

### 2. System Dependencies
```bash
# macOS
brew install portaudio

# Linux (Ubuntu/Debian)
sudo apt install portaudio19-dev espeak
```

</v-clicks>

---

# Setup Checklist (continued)

<v-clicks>

### 3. Ollama (local LLM)
```bash
# Download from https://ollama.com/download, then:
ollama pull qwen2.5:7b   # Recommended for agent labs
ollama pull gemma3:4b    # For vision lab
```

### 4. Clone the repo
```bash
git clone https://github.com/joakimeriksson/physical-agent.git
```

</v-clicks>

<v-click>

**No cloud API keys needed - everything runs locally!**

</v-click>

---
layout: center
---

# Foundation Labs

Everyone works through progressive exercises on their laptops

---

# Lab Overview

| Lab | Topic | What You'll Learn |
|-----|-------|-------------------|
| 1 | Speech | Whisper STT + Piper TTS |
| 2 | Vision | YOLO 11 object detection |
| 3 | Agent | Pydantic AI + Ollama function calling |
| 4 | Business | Vision + Speech + VLM combined |
| 5 | MCP | MCP server pattern |
| 6 | IoT | Remote MCP to IKEA DIRIGERA |
| 7 | Voice | Voice pipeline integration |
| 8 | A2A | Agent-to-agent communication |
| 9 | Voice IoT | Voice + A2A for smart home |
| 10 | Registry | A2A agent discovery |

---

# Lab 1: Speech

### Your AI Learns to Hear and Speak

```python
# Speech-to-Text with Whisper.cpp (local)
from pywhispercpp.model import Model
model = Model("base")
segments = model.transcribe("audio.wav")
text = " ".join([s.text for s in segments])

# Text-to-Speech with Piper (neural voices)
import subprocess
subprocess.run(["piper", "--output_file", "out.wav"],
               input=text.encode())
```

<v-click>

```bash
cd labs/lab1_speech && pixi run demo
```

</v-click>

---

# Lab 2: Vision

### Your AI Learns to See

```python
from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")  # 80 object classes
cap = cv2.VideoCapture(0)   # Webcam

while True:
    ret, frame = cap.read()
    results = model(frame)
    annotated = results[0].plot()
    cv2.imshow("YOLO", annotated)
```

<v-click>

```bash
cd labs/lab2_vision && pixi run demo
```

</v-click>

---

# Lab 3: AI Agent

### Your AI Learns to Use Tools

```python
from pydantic_ai import Agent

agent = Agent(
    "ollama:qwen3:4b",  # Local LLM
    system_prompt="You help with tasks using tools"
)

@agent.tool
def get_weather(city: str) -> str:
    """Get current weather for a city"""
    return f"Weather in {city}: 22°C, sunny"

result = agent.run_sync("What's the weather in Stockholm?")
```

<v-click>

```bash
cd labs/lab3_agent && pixi run demo
```

</v-click>

---

# Lab 4: Business Coach

### Multi-Modal Agent in Action

Combines everything:
- **Vision** → Camera analyzes your appearance
- **Speech** → Whisper transcribes your pitch
- **VLM** → Vision-language model gives feedback
- **TTS** → Speaks coaching advice

<v-click>

```
You: [Stand in front of camera, deliver pitch]
AI: "Good energy! Try making more eye contact.
     Your posture could be more confident.
     The content was clear but speak slower."
```

</v-click>

<v-click>

```bash
cd labs/lab4_business && pixi run demo
```

</v-click>

---

# Lab 5: MCP Server

### Create Your Own Tool Server

```python
from fastmcp import FastMCP

mcp = FastMCP("my-tools")

@mcp.tool()
def calculate(expression: str) -> float:
    """Evaluate a math expression"""
    return eval(expression)

@mcp.tool()
def get_time() -> str:
    """Get current time"""
    from datetime import datetime
    return datetime.now().isoformat()
```

<v-click>

Any MCP-compatible agent can discover and use these tools!

```bash
cd labs/lab5_mcp && pixi run demo
```

</v-click>

---

# Lab 6: IoT Control

### Connect to Real Devices

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

# Connect to remote DIRIGERA MCP server
mcp_server = MCPServerStreamableHTTP("http://dirigera.local:8000/mcp")

agent = Agent("ollama:qwen3:4b", mcp_servers=[mcp_server])

# Now your agent can control IKEA devices!
result = agent.run_sync("Turn on the living room light")
```

<v-clicks>

- Control real IKEA lights, sensors, blinds
- Natural language → device actions
- **Challenge:** Add voice control from Lab 1!

</v-clicks>

---

# Lab 7: Voice Agent

### Combine Speech + Agent

```python
from main import listen, speak  # From Lab 1
from pydantic_ai import Agent

agent = Agent("ollama:qwen3:4b")

@agent.tool
def get_time() -> str:
    from datetime import datetime
    return datetime.now().strftime("%H:%M")

while True:
    text = listen()              # Hear
    result = agent.run_sync(text)  # Think
    speak(result.output)         # Speak
```

<v-click>

```bash
cd labs/lab7_voice && pixi run demo
```

</v-click>

---

# Lab 8: A2A Protocol

### Agent-to-Agent Communication

```
┌─────────────────┐     A2A HTTP      ┌─────────────────┐
│   Agent A       │ ←───────────────→ │   Agent B       │
│   (Client)      │                   │   (Server)      │
└─────────────────┘                   └─────────────────┘
```

<v-clicks>

- **A2A** = Agent-to-Agent protocol by Google
- Agents discover each other via **Agent Cards**
- Exchange messages over HTTP/JSON-RPC
- pydantic-ai has built-in A2A support: `agent.to_a2a()`

</v-clicks>

<v-click>

```bash
cd labs/lab8_a2a && pixi run agent-b  # Terminal 1
cd labs/lab8_a2a && pixi run agent-a  # Terminal 2
```

</v-click>

---

# Lab 9: Voice + IoT via A2A

### The Ultimate Integration

```
    [Microphone]
         │
         ▼
    [Whisper STT]
         │
         ▼
    [A2A Client] ──────► [IoT Agent] ──► Smart Home
         │
         ▼
    [Piper TTS]
         │
         ▼
    [Speaker]
```

<v-click>

Control your smart home with voice via agent-to-agent communication!

```bash
cd labs/lab9_voice_iot && pixi run iot-agent  # Terminal 1
cd labs/lab9_voice_iot && pixi run demo       # Terminal 2
```

</v-click>

---

# Lab 10: Agent Registry

### Discover and Share Agents

<div class="grid grid-cols-2 gap-4">

<div>

```python
# Register your agent
from register import register
register(
    "http://registry:8000",
    "http://your-ip:9999"
)
```

- Central registry for the lab
- Web UI to see all agents
- Send messages to any agent
- Health-checking keeps it fresh

</div>

<div>

```
┌──────────────────────┐
│   Agent Registry     │
│   ┌──────────────┐   │
│   │ Tool Agent   │   │
│   │ IoT Agent    │   │
│   │ Your Agent!  │   │
│   └──────────────┘   │
│   [Chat] [Card]      │
└──────────────────────┘
```

</div>

</div>

<v-click>

```bash
cd labs/lab10_registry && pixi run registry
```

</v-click>

---
layout: center
class: text-center
---

# Lab Time!

**Part 1:** Foundation Labs on your laptop (~2 hours)

**Part 2:** Station rotation with physical devices (~1.5 hours)

---

# Part 2: Station Rotation

Groups rotate through 3 physical device stations (~30 min each)

| Station | Device | Experience |
|---------|--------|------------|
| 🍬 Candytron | Niryo Ned 2 robot arm | Vision + Speech + Robot control |
| 🤖 Reachy Mini | Expressive robot head | Look and interact |
| 💡 IKEA Smart Home | DIRIGERA hub | Real IoT device control |

<v-click>

### At Each Station
1. Connect your agent to the device
2. Explore the available tools
3. Create multi-modal interactions
4. **Get candy from the Candytron!**

</v-click>

---
layout: center
class: text-center
---

# Let's Get Started!

<div class="text-2xl pt-8">

🍬 There will be candy 🍬

</div>

---
layout: center
class: text-center
---

# Resources

<div class="grid grid-cols-2 gap-8 text-left pt-8">

<div>

### Standards
- [A2A Protocol](https://google.github.io/A2A/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Pydantic AI](https://ai.pydantic.dev/)

</div>

<div>

### Tools
- [Ollama](https://ollama.com/)
- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [OpenAI Whisper](https://github.com/openai/whisper)

</div>

</div>

---
layout: center
class: text-center
---

# Questions?

**Joakim Eriksson**
RISE Research Institutes of Sweden
joakim.eriksson@ri.se

<div class="pt-8">

GitHub: **github.com/joakimeriksson/physical-agent**

</div>
