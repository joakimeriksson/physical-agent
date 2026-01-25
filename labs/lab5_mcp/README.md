# Lab 5: MCP Server + Agent

> **Physical Agent Lab Series**
> AI is moving from the digital world into the physical world. This lab introduces MCP (Model Context Protocol) - a standard for exposing tools to AI models.

Simple MCP server with tools, connected to a Pydantic AI agent.

## What it does

**MCP Server** (`server.py`) exposes 3 tools:
- `get_time` - Current date and time
- `get_system_info` - OS, platform, Python version
- `calculate` - Evaluate math expressions

**Agent** (`agent.py`) connects to the MCP server and:
- Discovers available tools
- Chats with user via Ollama LLM
- Calls MCP tools when needed
- Returns natural language responses

## Prerequisites

```bash
ollama pull qwen3:4b
```

## Setup

```bash
pixi install
```

## Usage

```bash
# Run the agent (starts MCP server automatically)
pixi run agent

# Or run server standalone (for testing)
pixi run server
```

## Example Session

```
Connecting to MCP server...
Available MCP tools: ['get_time', 'get_system_info', 'calculate']

MCP Agent ready! Using qwen3:4b
Type 'quit' to exit.

You: What time is it?
Agent: It's Friday, January 24th 2026, at 2:30 PM.

You: What's the square root of 144?
Agent: The square root of 144 is 12.

You: What system am I running on?
Agent: You're running on macOS (Darwin) on an ARM64 machine with Python 3.12.

You: quit
Goodbye!
```

## Components

- **MCP Server:** Python `mcp` library with stdio transport
- **MCP Client:** Connects to server, discovers and calls tools
- **Agent:** Pydantic AI with Ollama backend
- **LLM:** qwen3:4b (local)

## Model Options

Small models struggle with knowing when to use tools. Try larger models:

```bash
# Default (fast but less accurate)
pixi run agent

# Better tool use (requires more RAM)
OLLAMA_MODEL=llama3.1:8b pixi run agent
OLLAMA_MODEL=qwen3:4b pixi run agent
```

## Known Limitations

Small local LLMs (3B parameters) are inconsistent with tool calling.
Sometimes they call tools unnecessarily, sometimes they don't call them when needed.
Larger models (8B+) or cloud APIs (GPT-4, Claude) are more reliable.

## Architecture

```
                          User
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                      agent.py                          │
│  ┌──────────────┐          ┌───────────────────────┐   │
│  │ Pydantic AI  │◄────────►│     MCP Client        │   │
│  │    Agent     │          │  (stdio connection)   │   │
│  └──────┬───────┘          └───────────┬───────────┘   │
└─────────┼──────────────────────────────┼───────────────┘
          │                              │
          ▼                              ▼ stdio
┌──────────────────┐          ┌───────────────────────┐
│     Ollama       │          │      server.py        │
│  (qwen3:4b)   │          │      MCP Server       │
│                  │          │  ┌─────────────────┐  │
│  LLM decides     │          │  │ get_time        │  │
│  which tools     │          │  │ get_system_info │  │
│  to call         │          │  │ calculate       │  │
└──────────────────┘          │  └─────────────────┘  │
                              └───────────────────────┘
```

**Flow:**
1. Agent starts MCP server as subprocess
2. Connects via stdio, discovers available tools
3. User asks a question
4. Pydantic AI sends to Ollama LLM
5. LLM decides to call a tool → MCP client calls server
6. Tool result returned → LLM generates response
