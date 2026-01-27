#!/usr/bin/env python3
"""Lab 9: Voice + IoT via A2A Challenge

Combine your Voice Agent (Lab 7) with A2A (Lab 8) to control IoT devices.

Your task:
1. Add speech input/output (from Lab 7 / Lab 1)
2. Connect to IoT Agent via A2A (from Lab 8)
3. Build voice loop: listen -> A2A -> speak

Usage:
    # Terminal 1: Start IoT agent
    pixi run iot-agent

    # Terminal 2: Run your voice client
    pixi run demo
"""
import sys
from pathlib import Path

# Add lab1_speech to path for speech functions
sys.path.insert(0, str(Path(__file__).parent.parent / "lab1_speech"))

# TODO: Import speech functions from lab1_speech
# from main import listen, speak

# TODO: Import A2A client components (from lab8)
# import asyncio
# from uuid import uuid4
# import httpx
# from a2a.client import A2ACardResolver, A2AClient
# from a2a.types import MessageSendParams, SendMessageRequest

IOT_AGENT_URL = "http://localhost:9998"


async def ask_iot_agent(question: str) -> str:
    """Send a command to the IoT agent via A2A.

    Hint: Look at agent_a.py from Lab 8 for the pattern.

    Args:
        question: The voice command to send

    Returns:
        The IoT agent's response
    """
    # TODO: Implement A2A client communication
    #
    # Steps (from Lab 8):
    # 1. Create httpx.AsyncClient
    # 2. Use A2ACardResolver to get agent card
    # 3. Create A2AClient
    # 4. Build SendMessageRequest
    # 5. Send and extract response
    #
    # async with httpx.AsyncClient(timeout=30.0) as http_client:
    #     resolver = A2ACardResolver(httpx_client=http_client, base_url=IOT_AGENT_URL)
    #     agent_card = await resolver.get_agent_card()
    #     client = A2AClient(httpx_client=http_client, agent_card=agent_card)
    #     ...
    return f"TODO: Implement A2A communication for: {question}"


async def voice_iot_loop():
    """Voice loop that talks to IoT agent via A2A.

    Hints:
    - listen() for speech input (returns str)
    - ask_iot_agent(text) to send command via A2A
    - speak(response) for audio output
    """
    # TODO: Implement the voice-to-IoT loop
    #
    # while True:
    #     try:
    #         # 1. Listen for voice command
    #         text = listen(duration=5.0)
    #         if not text:
    #             continue
    #
    #         print(f"You said: {text}")
    #
    #         # 2. Send to IoT agent via A2A
    #         response = await ask_iot_agent(text)
    #         print(f"IoT Agent: {response}")
    #
    #         # 3. Speak the response
    #         speak(response)
    #
    #     except KeyboardInterrupt:
    #         print("\nGoodbye!")
    #         break

    print("Voice + IoT via A2A Challenge")
    print("=" * 40)
    print()
    print("Your mission: Control smart home devices with your voice!")
    print()
    print("Architecture:")
    print("  [Microphone] -> [Whisper] -> [A2A] -> [IoT Agent] -> [Piper] -> [Speaker]")
    print()
    print("Steps:")
    print("  1. Start IoT agent: pixi run iot-agent")
    print("  2. Implement ask_iot_agent() using Lab 8 patterns")
    print("  3. Implement voice_iot_loop() using Lab 1/7 patterns")
    print("  4. Test with voice commands!")
    print()
    print("Example commands to try:")
    print("  - 'List all devices'")
    print("  - 'Turn on the living room light'")
    print("  - 'What's the temperature?'")
    print("  - 'Close the blinds'")
    print()


def main():
    """Main entry point."""
    import asyncio
    asyncio.run(voice_iot_loop())


if __name__ == "__main__":
    main()
