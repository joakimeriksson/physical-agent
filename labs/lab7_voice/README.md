# Lab 7: Voice Agent (Challenge)

> **Physical Agent Lab Series**
> AI is moving from the digital world into the physical world. In this challenge lab, you'll combine speech (Lab 1) with AI agents (Lab 5/6) to create a voice-controlled assistant.

## The Challenge

Create an AI agent you can talk to! Combine:
- **Speech input** (Whisper STT from Lab 1)
- **AI reasoning** (Pydantic AI + MCP from Lab 5)
- **Speech output** (Piper TTS from Lab 1)

## Prerequisites

Complete Labs 1 and 5 first to understand the components.

```bash
# Ensure Ollama is running with a model
ollama pull qwen3:4b
```

## Setup

```bash
pixi install
pixi run download-models  # Pre-download speech models
```

## Your Task

Edit `main.py` to:

1. **Import speech functions** from Lab 1:
   ```python
   from main import listen, speak
   ```

2. **Create an MCP agent** (like Lab 5):
   ```python
   from pydantic_ai import Agent
   from pydantic_ai.mcp import MCPServerStdio

   mcp_server = MCPServerStdio(sys.executable, [str(server_script)])
   agent = Agent("ollama:qwen3:4b", toolsets=[mcp_server])
   ```

3. **Build the voice loop**:
   ```python
   async with agent:
       while True:
           text = listen()           # Hear
           result = await agent.run(text)  # Think
           speak(result.output)       # Speak
   ```

## Testing

```bash
pixi run demo
```

Try saying:
- "What time is it?"
- "Calculate 15 times 7"
- "What system am I running?"

## Solution Hints

If you get stuck, here's the general structure:

```python
import asyncio
import sys
from pathlib import Path

# Add lab1 to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lab1_speech"))
from main import listen, speak

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

async def run_voice_agent():
    server_script = Path(__file__).parent.parent / "lab5_mcp" / "server.py"
    mcp_server = MCPServerStdio(sys.executable, [str(server_script)])

    agent = Agent(
        "ollama:qwen3:4b",
        system_prompt="You are a helpful voice assistant. Be concise.",
        toolsets=[mcp_server],
    )

    async with agent:
        print("Voice agent ready! Speak...")
        while True:
            try:
                text = listen(duration=5.0)
                if text:
                    print(f"You said: {text}")
                    result = await agent.run(text)
                    print(f"Agent: {result.output}")
                    speak(result.output)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    asyncio.run(run_voice_agent())
```

## Architecture

```
    Microphone          Speaker
        │                   ▲
        ▼                   │
   ┌─────────┐        ┌─────────┐
   │ Whisper │        │  Piper  │
   │  (STT)  │        │  (TTS)  │
   └────┬────┘        └────▲────┘
        │                  │
        ▼                  │
   ┌──────────────────────────────┐
   │       Pydantic AI Agent      │
   │    ┌──────────────────────┐  │
   │    │    MCP Client        │  │
   │    └──────────┬───────────┘  │
   └───────────────┼──────────────┘
                   │
                   ▼
   ┌──────────────────────────────┐
   │    MCP Server (Lab 5)        │
   │    - get_time                │
   │    - calculate               │
   │    - get_system_info         │
   └──────────────────────────────┘
```

## Bonus Challenges

1. **Custom wake word**: Only respond when you hear "Hey Agent"
2. **Continuous listening**: Use voice activity detection
3. **IoT control**: Connect to Lab 6's IoT MCP server instead
4. **Multi-turn conversation**: Remember conversation history
