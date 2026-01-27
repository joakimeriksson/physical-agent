#!/usr/bin/env python3
"""Agent B - A2A Server with Tools (using pydantic-ai)

This agent exposes tools via A2A protocol using pydantic-ai's to_a2a().
Run this first, then run agent_a.py to talk to it.

Usage:
    pixi run agent-b
"""
import math
import os
from datetime import datetime

from pydantic_ai import Agent
from a2a.types import AgentProvider

# Use Ollama by default (local model)
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("PYDANTIC_AI_MODEL", "ollama:qwen3:4b")

# Create the agent with tools
agent = Agent(
    MODEL,
    system_prompt="""You are a helpful assistant with calculator and time tools.
When asked about time or date, use the get_time tool.
When asked to calculate something, use the calculate tool.
Keep responses brief and friendly.""",
)


@agent.tool_plain
def calculate(expression: str) -> str:
    """Evaluate a math expression safely.

    Args:
        expression: Math expression like "2 + 2" or "sqrt(144)"
    """
    allowed = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "round": round,
        "pow": pow,
    }
    try:
        expr = expression.strip()
        result = eval(expr, {"__builtins__": {}}, allowed)  # pylint: disable=eval-used
        return f"{expr} = {result}"
    except Exception as err:  # pylint: disable=broad-exception-caught
        return f"Error: {err}"


@agent.tool_plain
def get_time() -> str:
    """Get current date and time."""
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


# Expose the agent as an A2A server
app = agent.to_a2a(
    name="Tool Agent",
    description="An agent with calculator and time tools",
    url="http://localhost:9999",
    provider=AgentProvider(organization="Jfokus Lab", url="https://jfokus.se"),
)


if __name__ == "__main__":
    import uvicorn

    print("Starting Agent B (A2A Server) on port 9999...")
    print(f"Model: {MODEL}")
    print("Tools: calculate, get_time")
    print("\nRun 'pixi run agent-a' in another terminal to talk to this agent.\n")

    uvicorn.run(app, host="0.0.0.0", port=9999)
