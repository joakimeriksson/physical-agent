#!/usr/bin/env python3
"""Simple test script for A2A communication.

Tests basic connectivity to Agent B.

Usage:
    pixi run test
"""
import asyncio

from agent_a import ask_agent_b


async def test_agent_b():
    """Run test queries against Agent B."""
    print("Testing A2A communication with Agent B...")
    print("=" * 50)

    test_cases = [
        "What time is it?",
        "Calculate 2 + 2",
        "What's sqrt(144)?",
        "Calculate 3.14159 * 2",
    ]

    for question in test_cases:
        print(f"\nQ: {question}")
        try:
            response = await ask_agent_b(question)
            print(f"A: {response}")
        except Exception as err:  # pylint: disable=broad-exception-caught
            print(f"Error: {err}")

    print("\n" + "=" * 50)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_agent_b())
