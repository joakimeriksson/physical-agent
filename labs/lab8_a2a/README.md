# Lab 8: A2A Basics (Guided)

> **Physical Agent Lab Series**
> AI is moving from the digital world into the physical world. This lab introduces A2A (Agent-to-Agent) protocol - enabling AI agents to communicate with each other.

## What is A2A?

A2A (Agent-to-Agent) is a protocol for agents to discover each other and exchange messages. It's like HTTP for AI agents!

Key concepts:
- **Agent Card**: An agent's identity (name, skills, URL)
- **Tasks**: Async work units that agents process
- **Messages**: How agents communicate

## Architecture

```
┌─────────────────┐     A2A HTTP      ┌─────────────────┐
│   Agent A       │ ←───────────────→ │   Agent B       │
│   (Client)      │                   │   (Server)      │
│   Asks questions│                   │   LLM + Tools   │
│                 │                   │   Port 9999     │
└─────────────────┘                   └─────────────────┘
```

## Setup

```bash
pixi install
```

**Requirements:** Ollama running locally with `qwen3:4b` model (or set `PYDANTIC_AI_MODEL` env var).

## Usage

**Terminal 1 - Start Agent B (server):**
```bash
pixi run agent-b
```

**Terminal 2 - Run Agent A (client):**
```bash
pixi run agent-a
```

## Example Session

```
Terminal 1:
$ pixi run agent-b
Starting Agent B (A2A Server) on port 9999...
Model: ollama:qwen3:4b
Tools: calculate, get_time

Terminal 2:
$ pixi run agent-a
A2A Client - Talking to Agent B
========================================
Type your questions. Type 'quit' to exit.

You: What time is it?
Agent B: The current time is January 27, 2026 at 14:30:45.

You: Calculate sqrt(144)
Agent B: The square root of 144 is **12**.

You: What's 3.14159 * 2?
Agent B: The result of 3.14159 × 2 is **6.28318**.
```

## Code Walkthrough

### Agent B (Server) - Using pydantic-ai

The server uses pydantic-ai's `to_a2a()` to expose an agent:

```python
from pydantic_ai import Agent

# Create agent with tools
agent = Agent(
    "ollama:qwen3:4b",
    system_prompt="You are a helpful assistant with calculator and time tools.",
)

@agent.tool_plain
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    result = eval(expression, {"__builtins__": {}}, safe_math_funcs)
    return f"{expression} = {result}"

@agent.tool_plain
def get_time() -> str:
    """Get current time."""
    return f"Current time: {datetime.now()}"

# One line to expose as A2A server!
app = agent.to_a2a(
    name="Tool Agent",
    description="An agent with calculator and time tools",
    url="http://localhost:9999",
)
```

### Agent A (Client)

The client discovers and talks to Agent B using the A2A protocol:

```python
from a2a.client import A2ACardResolver, A2AClient

async def ask_agent_b(question: str) -> str:
    async with httpx.AsyncClient() as http_client:
        # 1. Discover agent
        resolver = A2ACardResolver(httpx_client=http_client, base_url="http://localhost:9999")
        agent_card = await resolver.get_agent_card()

        # 2. Create client and send message
        client = A2AClient(httpx_client=http_client, agent_card=agent_card)
        response = await client.send_message(request)

        # 3. Poll for task completion (A2A is async)
        task_id = response.root.result.id
        while True:
            task = await client.get_task(task_id)
            if task.status.state == "completed":
                return task.artifacts[0].parts[0].text
```

## A2A vs MCP vs Pydantic-AI

| Feature | MCP | A2A | Pydantic-AI |
|---------|-----|-----|-------------|
| Purpose | Tool exposure | Agent communication | Agent framework |
| Pattern | Client-Server | Peer-to-peer | Single agent |
| Discovery | Tools in server | Agent cards | N/A |
| Use case | LLM → Tools | Agent → Agent | Build agents |

**They work together!** Pydantic-AI agents can use MCP tools internally AND expose themselves via A2A using `to_a2a()`.

## Testing

Run automated tests:
```bash
pixi run test
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | Ollama API URL |
| `PYDANTIC_AI_MODEL` | `ollama:qwen3:4b` | Model to use |

## Next Steps

In Lab 9, you'll combine A2A with voice to create a voice-controlled agent that talks to an IoT agent!
