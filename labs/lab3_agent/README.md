# Lab 3: AI Agent

> **Physical Agent Lab Series**
> AI is moving from the digital world into the physical world. In this lab series, we explore how AI can control real devices - robot arms, smart homes, and more. Before controlling physical devices, we start with a simple agent that uses tools - the foundation of agentic AI.

AI agent with local LLM (Ollama) and function calling - fully offline.

## Prerequisites

1. Install Ollama: https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```

## Setup

```bash
pixi install
```

## Usage

```bash
pixi run demo                    # Interactive chat
pixi run run "what time is it?"  # Single query
```

## Tools

The agent has access to these tools:

| Tool | Description |
|------|-------------|
| `calculator` | Evaluate math expressions |
| `get_current_time` | Get current date/time |
| `system_info` | Get hostname, OS, Python version |
| `list_files` | List files in directory |
| `read_file` | Read text file contents |

## Example Queries

```
What is sqrt(144) * 3?
What time is it?
What system am I running on?
List the files in the current directory
Read the pixi.toml file
```

## How It Works

Uses [Pydantic AI](https://ai.pydantic.dev/) to:
1. Send user query to local Ollama LLM
2. LLM decides which tools to call (if any)
3. Tools execute and return results
4. LLM generates final response

## Limitations

**Small models are inconsistent with function calling.** The 3B model sometimes:
- Ignores tools and makes up answers
- Calls wrong tools or wrong parameters
- Hallucinates results instead of using tool output

This is a key learning: reliable tool use requires larger models (70B+) or cloud APIs. For physical agents controlling real devices, you'd want a more capable model to avoid unpredictable behavior.

## API

```python
from pydantic_ai import Agent

agent = Agent("ollama:llama3.2")

@agent.tool_plain
def my_tool(arg: str) -> str:
    """Tool description."""
    return f"Result for {arg}"

result = agent.run_sync("Use my tool with 'hello'")
print(result.data)
```
