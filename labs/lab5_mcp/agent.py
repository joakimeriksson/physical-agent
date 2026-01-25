#!/usr/bin/env python3
"""Pydantic AI Agent with MCP tools via native MCP client.

Usage:
    pixi run agent
"""

import asyncio
import os
import sys
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Ollama setup
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "qwen3:4b")


async def run_agent():
    """Run agent with MCP server as toolset."""

    # MCP server as subprocess
    server_script = Path(__file__).parent / "server.py"
    mcp_server = MCPServerStdio(sys.executable, [str(server_script)])

    # Create agent with MCP toolset - tools discovered automatically
    agent = Agent(
        f"ollama:{MODEL_NAME}",
        system_prompt=f"""You are a helpful assistant. You are {MODEL_NAME} running on Ollama.

You have tools available, but ONLY use them when specifically needed:
- get_time: ONLY for current time/date questions
- get_system_info: ONLY for computer/system questions
- calculate: ONLY for math calculations

For general questions or greetings - answer directly WITHOUT tools.
Be concise.""",
        toolsets=[mcp_server],
    )

    print("Starting MCP server...")

    async with agent:
        print(f"\nMCP Agent ready! Using {MODEL_NAME}")
        print("Type 'quit' to exit.\n")

        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break

            try:
                result = await agent.run(user_input)
                print(f"Agent: {result.output}\n")
            except Exception as err:  # pylint: disable=broad-exception-caught
                print(f"Error: {err}\n")


def main():
    """Main entry point for MCP agent."""
    asyncio.run(run_agent())


if __name__ == "__main__":
    main()
