---
theme: default
title: AI in the Physical World
info: |
  ## AI in the Physical World
  Hands-on lab at Jfokus 2026

  LLMs, Multimodal AI, and Edge Intelligence controlling real devices
author: Joakim Eriksson
keywords: AI, LLM, Robotics, IoT, Edge AI
highlighter: shiki
drawings:
  persist: false
transition: slide-left
mdc: true
---

# AI in the Physical World

## LLMs that See, Listen, and Act

<div class="pt-12">
  <span class="px-2 py-1 rounded">
    Jfokus 2026 - Hands-on Lab
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

# The Architecture

How do we connect AI to physical devices?

---

# The Brain: LLM with Tools

```python
from openai import OpenAI

@tool
def pick_candy(color: str) -> str:
    """Pick up a candy of the specified color from the table"""
    position = vision.find_candy(color)
    robot.move_to(position)
    robot.grip()
    robot.move_to(HANDOVER_POSITION)
    return f"Picked up {color} candy"

# LLM decides WHEN and HOW to use tools
response = llm.chat(
    messages=[{"role": "user", "content": "Can I have a red candy?"}],
    tools=[pick_candy, set_light, speak]
)
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

# MCP: Model Context Protocol

A standard way to give LLMs access to tools

---

# MCP Tools

```python
@mcp.tool()
async def control_light(
    device_id: str,
    brightness: int,
    color: str
) -> str:
    """Control an IKEA smart light"""
    await dirigera.set_light(device_id, brightness, color)
    return f"Light {device_id} set to {color} at {brightness}%"

@mcp.tool()
async def get_room_temperature() -> float:
    """Read temperature from IKEA sensor"""
    return await dirigera.read_sensor("temperature")
```

LLMs can discover and use these tools automatically

---
layout: center
---

# Foundation Labs

Everyone works through progressive exercises on their laptops

| Lab | Topic | What You'll Learn |
|-----|-------|-------------------|
| 1 | Speech | Whisper STT + Piper TTS |
| 2 | Vision | YOLO 11 object detection |
| 3 | Agent | Pydantic AI + Ollama function calling |
| 4 | Business | Vision + Speech + VLM combined |
| 5 | MCP | MCP server pattern |
| 6 | IoT | Remote MCP to IKEA DIRIGERA |
| 6+ | Challenge | Voice-controlled IoT |

---

# Lab 1: Speech

### Your AI Learns to Hear and Speak

```python
# Speech-to-Text with Whisper (local)
from faster_whisper import WhisperModel
model = WhisperModel("small")
segments, _ = model.transcribe("audio.wav")
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
from pydantic_ai.mcp import MCPServerHTTP

# Connect to remote DIRIGERA MCP server
mcp_server = MCPServerHTTP(url="http://dirigera.local:8000/sse")

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
1. Connect your agent to the MCP server
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

# Questions?

**Joakim Eriksson**
RISE Research Institutes of Sweden
joakim.eriksson@ri.se

<div class="pt-8">

GitHub: `github.com/joakimeriksson/mcp-agents`

</div>
