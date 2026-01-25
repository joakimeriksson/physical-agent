#!/usr/bin/env python3
"""Lab 3: AI Agent with Local LLM

Uses Pydantic AI with Ollama for fully local inference.
The agent has simple tools to demonstrate function calling.

Prerequisites:
    1. Install Ollama: https://ollama.ai
    2. Pull a model: ollama pull llama3.2

Usage:
    pixi run demo              # Interactive chat with agent
    pixi run run "your query"  # Single query
"""

import os
import sys
import math
from datetime import datetime

from pydantic_ai import Agent

# --- Agent Setup ---

# Set Ollama base URL for pydantic-ai
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# Using Ollama with a small local model
# Note: Small models (3-8B) are inconsistent with function calling
MODEL_NAME = "qwen3:4b"

agent = Agent(
    f"ollama:{MODEL_NAME}",
    system_prompt=f"""You are a helpful assistant running as model '{MODEL_NAME}' on Ollama.
You have access to tools - ALWAYS use them when asked about system info, time, files, or calculations.
NEVER make up information. If you don't know something, say so.
Be concise.""",
)


# --- Tools ---

@agent.tool_plain
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A math expression like "2 + 2" or "sqrt(16) * 3"
    """
    # Safe math evaluation
    allowed = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "round": round,
        "pow": pow,
    }
    try:
        # pylint: disable=eval-used  # Safe: restricted builtins
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"{expression} = {result}"
    except (ValueError, TypeError, SyntaxError, NameError) as e:
        return f"Error: {e}"


@agent.tool_plain
def get_current_time() -> str:
    """Get the current date and time."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S (%A)")


@agent.tool_plain
def get_current_model() -> str:
    """Get the current LLM model being used."""
    return f"Current model: {MODEL_NAME} (running locally via Ollama)"


@agent.tool_plain
def system_info() -> str:
    """Get system information (hostname, OS, Python version, Ollama models)."""
    import platform  # pylint: disable=import-outside-toplevel
    import subprocess  # pylint: disable=import-outside-toplevel

    info = [
        f"Current LLM: {MODEL_NAME}",
        f"Host: {platform.node()}",
        f"OS: {platform.system()} {platform.release()}",
        f"Python: {platform.python_version()}",
    ]

    # Get Ollama models
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5, check=False
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            models = [line.split()[0] for line in lines if line.strip()]
            info.append(f"Available Ollama models: {', '.join(models[:5])}")
    except (OSError, subprocess.TimeoutExpired):
        pass

    return "\n".join(info)


@agent.tool_plain
def list_files(directory: str = ".") -> str:
    """List files in a directory.

    Args:
        directory: Path to directory (default: current)
    """
    from pathlib import Path  # pylint: disable=import-outside-toplevel

    try:
        path = Path(directory)
        files = list(path.iterdir())
        if not files:
            return f"No files in {directory}"
        return "\n".join(
            f"  {f.name}" + ("/" if f.is_dir() else "") for f in files[:20]
        )
    except OSError as e:
        return f"Error: {e}"


@agent.tool_plain
def read_file(path: str) -> str:
    """Read contents of a text file.

    Args:
        path: Path to the file
    """
    from pathlib import Path  # pylint: disable=import-outside-toplevel

    try:
        content = Path(path).read_text(encoding="utf-8")
        if len(content) > 1000:
            return content[:1000] + "\n... (truncated)"
        return content
    except OSError as e:
        return f"Error: {e}"


# --- Main ---

def chat(debug: bool = False):
    """Interactive chat loop."""
    print("Chat with AI Agent (local Ollama)")
    print("Type 'quit' to exit, 'debug' to toggle debug mode\n")
    print("Tools: calculator, get_current_time, get_current_model,")
    print("       system_info, list_files, read_file\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break
        if user_input.lower() == "debug":
            debug = not debug
            print(f"Debug mode: {'ON' if debug else 'OFF'}\n")
            continue
        if not user_input:
            continue

        try:
            result = agent.run_sync(user_input)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error: {e}\n")
            continue

        if debug:
            _print_debug_info(result)

        print(f"Agent: {result.output}\n")


def _print_debug_info(result):
    """Print debug info about tool calls."""
    for msg in result.new_messages():
        if hasattr(msg, 'parts'):
            for part in msg.parts:
                if hasattr(part, 'tool_name'):
                    print(f"  [TOOL] {part.tool_name}({getattr(part, 'args', {})})")
                if hasattr(part, 'content') and part.content:
                    print(f"  [RESULT] {part.content[:100]}...")


def run_single(query: str):
    """Run a single query."""
    print(f"Query: {query}\n")
    result = agent.run_sync(query)
    print(f"Agent: {result.output}")


def main():
    """Main entry point for agent lab CLI."""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "chat":
        chat()
    elif cmd == "run":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Hello, what can you do?"
        run_single(query)
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
