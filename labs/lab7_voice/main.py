#!/usr/bin/env python3
"""Lab 7: Voice Agent Challenge

Combine Lab 1 (speech) with Lab 5/6 (MCP) to create a voice-controlled agent.

Your task:
1. Import listen() and speak() functions (hint: look at Lab 1)
2. Create an agent with MCP tools (hint: look at Lab 5/6)
3. Build a voice loop: listen -> agent -> speak

Usage:
    pixi run demo
"""
import sys
from pathlib import Path

# Add lab1_speech to path so we can import speech functions
sys.path.insert(0, str(Path(__file__).parent.parent / "lab1_speech"))

# TODO: Import speech functions from lab1_speech
# from main import listen, speak

# TODO: Import agent components (hint: look at lab5_mcp/agent.py)
# import asyncio
# import os
# from pydantic_ai import Agent
# from pydantic_ai.mcp import MCPServerStdio

# TODO: Set up Ollama model
# os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434/v1")
# MODEL_NAME = os.environ.get("OLLAMA_MODEL", "qwen3:4b")


def voice_agent_loop():
    """Main voice agent loop.

    Hints:
    - Use listen() to get user speech as text (returns str)
    - Use agent.run_sync(text) to get agent response
    - Use speak() to say the response aloud

    Example flow:
        while True:
            text = listen(duration=5.0)
            if text:
                result = agent.run_sync(text)
                speak(result.output)
    """
    # TODO: Implement the voice loop
    #
    # Steps:
    # 1. Create an MCP server pointing to lab5's server.py:
    #    server_script = Path(__file__).parent.parent / "lab5_mcp" / "server.py"
    #    mcp_server = MCPServerStdio(sys.executable, [str(server_script)])
    #
    # 2. Create an agent with the MCP toolset:
    #    agent = Agent(
    #        f"ollama:{MODEL_NAME}",
    #        system_prompt="You are a helpful voice assistant. Keep responses brief.",
    #        toolsets=[mcp_server],
    #    )
    #
    # 3. Run the agent in an async context and loop:
    #    async with agent:
    #        while True:
    #            text = listen()
    #            result = await agent.run(text)
    #            speak(result.output)
    #
    # 4. Don't forget to handle KeyboardInterrupt for clean exit!

    print("Voice Agent Challenge")
    print("=" * 40)
    print()
    print("Your mission: Make an AI that listens, thinks, and speaks!")
    print()
    print("Hints:")
    print("  - Lab 1 has listen() and speak() functions")
    print("  - Lab 5 has the MCP agent pattern")
    print("  - Combine them into a voice loop")
    print()
    print("Look at the TODOs in this file to get started.")
    print()


def main():
    """Main entry point."""
    voice_agent_loop()


if __name__ == "__main__":
    main()
