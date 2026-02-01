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
---

# The Next Step: Physical AI Evolution

Where is this all heading?

---

# LLMs + Function Calling

<div class="grid grid-cols-2 gap-8">

<div>

### The Foundation

LLMs can reason and decide **when** to act:

<v-clicks>

- Text in → text out, but with **tool use**
- LLM decides which function to call
- Structured outputs (JSON) for actions
- Works today with Ollama, GPT-4, Claude

</v-clicks>

</div>

<div>

### Example

```python
@agent.tool
def turn_on_light(room: str) -> str:
    """Turn on light in a room"""
    return set_light(room, on=True)

# LLM decides to call this tool
agent.run("It's getting dark in here")
# → calls turn_on_light("living room")
```

<v-click>

**Limitation:** LLM can't see the world

</v-click>

</div>

</div>

---

# Vision-Language Models (VLMs)

<div class="grid grid-cols-2 gap-8">

<div>

### Adding Eyes to LLMs

Now the model can **see** and reason:

<v-clicks>

- Image + text in → text out
- Understands scenes, objects, text in images
- Can describe what it sees
- Still needs function calling to act

</v-clicks>

</div>

<div>

### Example

```python
# VLM can see and reason
response = vlm.run(
    image=camera.capture(),
    prompt="What candy colors do you see?"
)
# → "I see red, green, and yellow candies"

# Still needs tools to act
@agent.tool
def pick_candy(color: str): ...
```

<v-click>

**Limitation:** Separate vision and action

</v-click>

</div>

</div>

<v-click>

**Models:** LLaVA, Qwen2-VL, GPT-4V, Gemini Pro Vision, Claude

</v-click>

---

# Vision-Language-Action (VLA) Models

<div class="grid grid-cols-2 gap-8">

<div>

### The New Paradigm

Instead of separate models for vision, language, and control:

<v-clicks>

- **One model** that sees, understands, and acts
- Trained on robot demonstration data
- Natural language instructions → robot actions
- Generalizes across tasks and environments

</v-clicks>

</div>

<div>

### Key Models

<v-clicks>

- **OpenVLA** (Stanford) - 7B params, open-source
  - Outperforms RT-2-X with 7× fewer params
- **π0** (Physical Intelligence) - 3B VLM + diffusion
  - 50Hz continuous control
  - Remarkable dexterity
- **RT-2** (Google) - Pioneer VLA

</v-clicks>

</div>

</div>

<v-click>

[arxiv.org/abs/2406.09246](https://arxiv.org/abs/2406.09246) | [learnopencv.com/vision-language-action-models](https://learnopencv.com/vision-language-action-models-lerobot-policy/)

</v-click>

---

# V-JEPA 2: World Models for Robots

<div class="grid grid-cols-2 gap-8">

<div>

### Meta's Approach

<v-clicks>

- **World model** trained on 1M+ hours of video
- Learns physics from watching the world
- Predicts what happens next
- Zero-shot robot control in new environments
- 65-80% success on pick-and-place tasks

</v-clicks>

</div>

<div>

### Why It Matters

<v-clicks>

- No task-specific training needed
- Only 62 hours of robot video required
- 30× faster than alternatives (Nvidia Cosmos)
- Understands cause and effect
- "Common sense" for robots

</v-clicks>

</div>

</div>

<v-click>

[ai.meta.com/blog/v-jepa-2-world-model-benchmarks](https://ai.meta.com/blog/v-jepa-2-world-model-benchmarks/)

</v-click>

---

# Humanoid Robots: 2026 Reality

<div class="grid grid-cols-3 gap-4 text-sm">

<div class="text-center">

<img src="/optimus.webp" class="h-32 mx-auto rounded shadow mb-2" />

### Tesla Optimus
- Gen 3 deployed in factories
- Target: 50,000 units in 2026
- Price goal: $20-30K

</div>

<div class="text-center">

<img src="/neo.jpg" class="h-32 mx-auto rounded shadow mb-2" />

### 1X NEO
- Consumer home robot
- Pre-orders open: $20K
- Soft, safe design (30kg)

</div>

<div class="text-center">

<img src="/figure02.webp" class="h-32 mx-auto rounded shadow mb-2" />

### Figure 02/03
- BMW factory deployment
- Enterprise focus (>$100K)
- OpenAI partnership

</div>

</div>

<v-click>

<div class="pt-4 text-center">

**The shift:** From research demos → commercial deployment

</div>

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

### The Idea
Connect multiple AI models into a system that:
- Involves **human interaction** (speech)
- Has **effects on the real world** (robot arm)
- Runs **only local models** on a laptop with GPU

::right::

<div class="pt-4">

### Hardware: Niryo Ned 2
- 6-axis collaborative robot arm
- Gripper for candy manipulation
- External camera (YOLO detection)
- Microphone (Whisper STT)
- Speaker (Piper TTS)
- Configure & modify via web UI

</div>

---
layout: two-cols
---

# Candytron 4000

### How It Works

```
   "Give me red candy"
          │
          ▼
   ┌──────────────┐
   │ Whisper STT  │
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  YOLO Vision │ ◄── candy positions
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  LLM + Tools │ ◄── pick red @ (x,y)
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  Robot Arm   │ ◄── grip & deliver
   └──────────────┘
```

::right::

<div class="pt-12 pl-4">

### AI Components
- **Whisper** → Speech-to-text
- **YOLO 11** → Detect candy positions
- **Ollama LLM** → Reasoning + pick action
- **Piper** → Text-to-speech

All running locally!

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
- Natural voice interaction
- Configure & modify via web UI

::right::

<div class="flex items-center justify-center h-full">

<img src="/reachy-mini.png" class="h-80 rounded shadow" />

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

**Build your own agent to control real devices!**

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

<div class="flex justify-center">
<img src="/a2a-mcp.png" class="h-72 rounded shadow" />
</div>

<div class="grid grid-cols-2 gap-8 pt-4 text-sm">

<div>

**MCP** = Vertical integration (Agent → Tools)
- Agent connects to tools, databases, APIs

</div>

<div>

**A2A** = Horizontal integration (Agent ↔ Agent)
- Agents discover and collaborate with each other

</div>

</div>

<div class="text-xs opacity-50 pt-4">

Source: [blog.logto.io/a2a-mcp](https://blog.logto.io/a2a-mcp)

</div>

---

# MCP: Model Context Protocol

<div class="grid grid-cols-2 gap-8">

<div>

**By Anthropic** - Like USB-C for AI

<v-clicks>

- **Tools**: Functions the LLM can call
- **Resources**: Structured data access
- **Prompts**: Reusable templates
- Transport: stdio, HTTP (streamable)

</v-clicks>

</div>

<div>

```python
from fastmcp import FastMCP

mcp = FastMCP("iot-tools")

@mcp.tool()
def turn_on_light(room: str) -> str:
    """Turn on light in a room"""
    dirigera.set_light(room, on=True)
    return f"Light in {room} is now on"

# Any MCP client can discover & use this!
```

</div>

</div>

<v-click>

**Why it matters:** Your agent can use ANY MCP server - IoT, databases, APIs...

</v-click>

---

# A2A: Agent-to-Agent Protocol

<div class="grid grid-cols-2 gap-8">

<div>

**By Google + 50 partners** - Agents talking to agents

<v-clicks>

- **Agent Cards**: JSON describing capabilities
- **Tasks**: Request/response with lifecycle
- **Artifacts**: Rich data exchange
- **Security**: OAuth 2.0, API keys built-in

</v-clicks>

</div>

<div>

```python
from pydantic_ai import Agent

agent = Agent("ollama:qwen3:4b")

@agent.tool
def get_weather(city: str) -> str:
    return f"Weather in {city}: 22°C"

# Expose as A2A server
app = agent.to_a2a()

# Other agents can now discover and
# send tasks to this agent!
```

</div>

</div>

<v-click>

**Why it matters:** Your voice agent can delegate to an IoT agent, which delegates to a weather agent...

</v-click>

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
1. **Hear** → Whisper transcribes "Can I have a red candy?"
2. **See** → YOLO detects all candy positions
3. **Think** → LLM picks red candy at (x,y)
4. **Act** → Robot grips and delivers
5. **Speak** → TTS says "Here's your red candy!"

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

# Windows PowerShell (run as Administrator)
powershell -ExecutionPolicy ByPass -c "irm https://pixi.sh/install.ps1 | iex"

# Windows alternative (recommended):
winget install prefix-dev.pixi
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

<div class="grid grid-cols-2 gap-8 text-sm">

<div>

| Lab | Topic | What You'll Learn |
|-----|-------|-------------------|
| 1 | Speech | Whisper STT + Piper TTS |
| 2 | Vision | YOLO 11 object detection |
| 3 | Agent | Pydantic AI + Ollama |
| 4 | Business | Vision + Speech + VLM |
| 5 | MCP | MCP server pattern |

</div>

<div>

| Lab | Topic | What You'll Learn |
|-----|-------|-------------------|
| 6 | IoT | Remote MCP to DIRIGERA |
| 7 | Voice | Voice pipeline integration |
| 8 | A2A | Agent-to-agent protocol |
| 9 | Voice IoT | Voice + A2A smart home |
| 10 | Registry | A2A agent discovery |

</div>

</div>

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

Combines vision + speech output:
- **Camera** → Captures your photo
- **VLM** → Analyzes clothing, grooming, background, pose
- **TTS** → Speaks the feedback aloud

<v-click>

```
CLOTHING:   3/10  "Hoodie and ripped jeans are inappropriate"
GROOMING:   3/10  "Hair is quite messy"
BACKGROUND: 3/10  "Bookshelf is a bit overwhelming"
POSE:       4/10  "Slumped somewhat, doesn't project confidence"
────────────────────────────────────────
AVERAGE:    3.2/10
"Hmm, might want to do a bit more preparation..."
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
| 🍬 Candytron | Niryo Ned 2 robot arm | Interact via voice & video, configure via web UI |
| 🤖 Reachy Mini | Expressive robot head | Interact via voice & video, configure via web UI |
| 💡 IKEA Smart Home | DIRIGERA hub | **Build & connect your own agent!** |

<v-click>

### At Each Station
- **Candytron & Reachy Mini:** Talk to the robots, watch them respond, tweak settings via laptop
- **IKEA Smart Home:** Connect your agent from Lab 6 to real devices
- **Get candy from the Candytron!**

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
