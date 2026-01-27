# Lab 9: Voice + IoT via A2A (Challenge)

> **Physical Agent Lab Series**
> AI is moving from the digital world into the physical world. This is the ultimate challenge: voice-controlled smart home via agent-to-agent communication!

## The Challenge

Create a voice interface for your smart home by combining:
- **Voice input/output** (Lab 1 / Lab 7)
- **A2A protocol** (Lab 8)
- **IoT control** (provided IoT agent)

## Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                      Your Voice Client                        │
│                                                               │
│   Microphone ──► Whisper STT ──► A2A Client ──► Piper TTS ──► Speaker
│                                      │
└──────────────────────────────────────┼────────────────────────┘
                                       │
                                       ▼ A2A HTTP
┌───────────────────────────────────────────────────────────────┐
│                      IoT Agent (provided)                     │
│                                                               │
│   Simulated DIRIGERA Hub:                                     │
│   - Living room light                                         │
│   - Bedroom light                                             │
│   - Kitchen light                                             │
│   - Temperature sensor                                        │
│   - Bedroom blinds                                            │
└───────────────────────────────────────────────────────────────┘
```

## Prerequisites

Complete Labs 1, 7, and 8 first.

## Setup

```bash
pixi install
pixi run download-models  # Pre-download speech models
```

## Usage

**Terminal 1 - Start IoT agent:**
```bash
pixi run iot-agent
```

**Terminal 2 - Run your voice client:**
```bash
pixi run demo
```

## Your Task

Edit `voice_client.py` to:

### 1. Import required modules

```python
# Speech from Lab 1
from main import listen, speak

# A2A from Lab 8
import asyncio
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest
```

### 2. Implement `ask_iot_agent()`

```python
async def ask_iot_agent(question: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        resolver = A2ACardResolver(
            httpx_client=http_client,
            base_url=IOT_AGENT_URL
        )
        agent_card = await resolver.get_agent_card()
        client = A2AClient(httpx_client=http_client, agent_card=agent_card)

        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(
                message={
                    "role": "user",
                    "parts": [{"kind": "text", "text": question}],
                    "messageId": uuid4().hex,
                }
            ),
        )

        response = await client.send_message(request)

        if response.result and response.result.parts:
            for part in response.result.parts:
                if hasattr(part, "text"):
                    return part.text
        return str(response)
```

### 3. Implement `voice_iot_loop()`

```python
async def voice_iot_loop():
    print("Voice IoT Control Ready!")
    print("Speak your commands...\n")

    while True:
        try:
            text = listen(duration=5.0)
            if not text:
                continue

            print(f"You said: {text}")
            response = await ask_iot_agent(text)
            print(f"IoT Agent: {response}")
            speak(response)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
```

## Example Session

```
$ pixi run demo
Voice IoT Control Ready!
Speak your commands...

Recording 5s...
Transcribing...
You said: list all devices
IoT Agent: Available IoT devices:
  - living_room_light (light): off (brightness: 0%)
  - bedroom_light (light): on (brightness: 80%)
  - kitchen_light (light): off (brightness: 0%)
  ...

Recording 5s...
Transcribing...
You said: turn on the living room light
IoT Agent: Turned on living_room_light

Recording 5s...
Transcribing...
You said: what's the temperature
IoT Agent: Current temperature: 21.3C
```

## IoT Agent Commands

The provided IoT agent understands:

| Command | Example |
|---------|---------|
| List devices | "List all devices", "What devices do you have?" |
| Light on/off | "Turn on living room light", "Switch off kitchen light" |
| Light brightness | "Set bedroom light to 50%" |
| Temperature | "What's the temperature?", "How warm is it?" |
| Blinds | "Open the blinds", "Close the blinds", "Set blinds to 50%" |

## Bonus Challenges

1. **Wake word**: Only respond after hearing "Hey home"
2. **Continuous mode**: Keep listening without fixed duration
3. **Real DIRIGERA**: Connect to actual IKEA hub instead of simulator
4. **Multiple rooms**: Add room context awareness
5. **Scenes**: Add "movie mode" (dim lights, close blinds)

## Troubleshooting

**"Cannot connect to IoT Agent"**
- Make sure `pixi run iot-agent` is running in another terminal

**"No speech detected"**
- Speak clearly and close to microphone
- Adjust `duration` parameter in `listen()`

**"Slow response"**
- First run downloads models (~200MB)
- Subsequent runs use cached models

## Full Solution

If completely stuck, here's the complete solution:

```python
#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent / "lab1_speech"))
from main import listen, speak

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

IOT_AGENT_URL = "http://localhost:9998"


async def ask_iot_agent(question: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        resolver = A2ACardResolver(httpx_client=http_client, base_url=IOT_AGENT_URL)
        agent_card = await resolver.get_agent_card()
        client = A2AClient(httpx_client=http_client, agent_card=agent_card)

        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(
                message={
                    "role": "user",
                    "parts": [{"kind": "text", "text": question}],
                    "messageId": uuid4().hex,
                }
            ),
        )
        response = await client.send_message(request)

        if response.result and response.result.parts:
            for part in response.result.parts:
                if hasattr(part, "text"):
                    return part.text
        return str(response)


async def voice_iot_loop():
    print("Voice IoT Control Ready!")
    print("Speak your commands. Ctrl+C to exit.\n")

    while True:
        try:
            text = listen(duration=5.0)
            if not text:
                continue

            print(f"You said: {text}")
            response = await ask_iot_agent(text)
            print(f"IoT Agent: {response}\n")
            speak(response)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except httpx.ConnectError:
            print("Error: IoT Agent not running. Start with: pixi run iot-agent")
            break


if __name__ == "__main__":
    asyncio.run(voice_iot_loop())
```
