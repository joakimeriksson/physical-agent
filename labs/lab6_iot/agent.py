#!/usr/bin/env python3
"""IoT Agent - connects to remote MCP server using Pydantic AI's native MCP client.

Usage:
    pixi run agent
    pixi run agent --server http://192.168.1.100:8000/mcp
"""

import argparse
import asyncio
import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

# Ollama setup
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "qwen3:4b")

DEFAULT_SERVER = "http://localhost:8000/mcp/"


async def run_agent(server_url: str):
    """Run IoT agent with MCP toolset."""

    # Create MCP server connection as a toolset
    mcp_server = MCPServerStreamableHTTP(server_url)

    # Create agent with MCP toolset - tools are discovered automatically
    agent = Agent(
        f"ollama:{MODEL_NAME}",
        system_prompt="""You are a smart home assistant controlling IKEA devices.
Use your tools to list and control lights, outlets, and sensors.
Always list devices first before trying to control them.
Be concise.""",
        toolsets=[mcp_server],
    )

    print(f"Connecting to MCP server: {server_url}")

    try:
        async with agent:
            # Tools are now available from the MCP server
            print(f"\nIoT Agent ready! Using {MODEL_NAME}")
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
    except BaseException:  # pylint: disable=broad-except
        pass  # Suppress MCP client cleanup errors (ExceptionGroup in Python 3.11+)


def main():
    """Main entry point for IoT agent CLI."""
    parser = argparse.ArgumentParser(description='IoT Agent - control smart home via MCP')
    parser.add_argument('--server', default=DEFAULT_SERVER,
                        help=f'MCP server URL (default: {DEFAULT_SERVER})')
    args = parser.parse_args()

    asyncio.run(run_agent(args.server))


if __name__ == "__main__":
    main()
