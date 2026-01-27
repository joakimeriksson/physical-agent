#!/usr/bin/env python3
"""Agent A - A2A Client

This agent connects to Agent B and asks questions.
First run agent_b.py, then run this script.

Usage:
    pixi run agent-a
"""
import asyncio
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest, GetTaskRequest


async def ask_agent_b(
    question: str,
    base_url: str = "http://localhost:9999",
    timeout: float = 60.0,
) -> str:
    """Send a question to Agent B and get response.

    Args:
        question: The question to ask
        base_url: Agent B's URL (default: localhost:9999)
        timeout: Max time to wait for response

    Returns:
        The agent's response text
    """
    async with httpx.AsyncClient(timeout=timeout) as http_client:
        # Step 1: Discover Agent B by fetching its agent card
        resolver = A2ACardResolver(
            httpx_client=http_client,
            base_url=base_url,
        )
        agent_card = await resolver.get_agent_card()

        # Step 2: Create an A2A client for Agent B
        client = A2AClient(httpx_client=http_client, agent_card=agent_card)

        # Step 3: Build and send the message
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(
                message={
                    "role": "user",
                    "parts": [{"kind": "text", "text": question}],
                    "messageId": uuid4().hex,
                }
            ),
        )

        response = await client.send_message(request)

        # Step 4: Get task ID and poll for completion
        result = response.root.result if hasattr(response, "root") else response.result

        # If result is a Task, poll until completed
        if hasattr(result, "id") and hasattr(result, "status"):
            task_id = result.id
            # Poll for task completion
            for _ in range(30):  # Max 30 attempts
                task_request = GetTaskRequest(
                    id=str(uuid4()),
                    params={"id": task_id},
                )
                task_response = await client.get_task(task_request)
                task = task_response.root.result if hasattr(task_response, "root") else task_response.result

                if hasattr(task, "status") and hasattr(task.status, "state"):
                    state = str(task.status.state.value) if hasattr(task.status.state, "value") else str(task.status.state)
                    if state == "completed":
                        # Extract from artifacts
                        if hasattr(task, "artifacts") and task.artifacts:
                            for artifact in task.artifacts:
                                if hasattr(artifact, "parts"):
                                    for part in artifact.parts:
                                        if hasattr(part, "root") and hasattr(part.root, "text"):
                                            return part.root.text
                                        if hasattr(part, "text"):
                                            return part.text
                        return "Task completed but no response text found"
                    if state in ("failed", "canceled"):
                        return f"Task {state}: {getattr(task.status, 'message', 'No details')}"

                await asyncio.sleep(1)

            return "Timeout waiting for response"

        # Direct message response (old-style)
        if hasattr(result, "parts") and result.parts:
            for part in result.parts:
                if hasattr(part, "root") and hasattr(part.root, "text"):
                    return part.root.text
                if hasattr(part, "text"):
                    return part.text

        return str(response)


async def main():
    """Interactive client that talks to Agent B."""
    print("A2A Client - Talking to Agent B")
    print("=" * 40)
    print("Type your questions. Type 'quit' to exit.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        try:
            response = await ask_agent_b(question)
            print(f"Agent B: {response}\n")
        except httpx.ConnectError:
            print("Error: Cannot connect to Agent B. Is it running on port 9999?\n")
            print("Start it with: pixi run agent-b\n")
        except Exception as err:  # pylint: disable=broad-exception-caught
            print(f"Error: {err}\n")


if __name__ == "__main__":
    asyncio.run(main())
