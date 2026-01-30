#!/usr/bin/env python3
"""Candytron 4000 - A2A Agent (Virtual/Simulated)

A candy-dispensing robot agent that registers with the A2A registry.
This is a VIRTUAL version with canned responses for testing.

=== INTEGRATION POINTS FOR REAL CANDYTRON ===

To connect the real Candytron 4000:

1. Robot Control (Niryo Ned 2):
   - See pick_candy() tool - replace mock with pyniryo calls
   - Import: from pyniryo import NiryoRobot

2. Camera/Vision (YOLO):
   - See see_candy() tool - replace mock with real camera + YOLO
   - Import: from ultralytics import YOLO
   - Import: import cv2

3. Speech (TTS):
   - See speak() tool - replace mock with Piper TTS
   - Import: from piper import PiperVoice

4. Microphone (STT):
   - A2A can receive audio via FilePart
   - Add Whisper transcription in voice handler

See robot.py for integration stubs.

Usage:
    pixi run agent

    # With registry
    REGISTRY_URL=http://localhost:8000 pixi run agent
"""

import base64
import os
import threading
import time
from pathlib import Path

import httpx
import uvicorn
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from a2a.types import AgentSkill, AgentProvider

# --- Configuration ---

os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("PYDANTIC_AI_MODEL", "ollama:gemma3:4b")
REGISTRY_URL = os.environ.get("REGISTRY_URL", "http://localhost:8000")
AGENT_PORT = int(os.environ.get("CANDYTRON_PORT", "9999"))
AGENT_URL = os.environ.get("CANDYTRON_URL", f"http://localhost:{AGENT_PORT}")

# Path to canned camera image (placed in this directory)
CANNED_IMAGE_PATH = Path(__file__).parent / "candy_table.jpg"


# --- Virtual/Canned Responses ---

CANNED_CANDY = [
    {"color": "red", "type": "gummy bear", "x": 120, "y": 80},
    {"color": "blue", "type": "lollipop", "x": 250, "y": 100},
    {"color": "green", "type": "gummy bear", "x": 180, "y": 150},
    {"color": "yellow", "type": "jelly bean", "x": 300, "y": 90},
    {"color": "orange", "type": "candy corn", "x": 80, "y": 120},
]


def get_canned_image_base64() -> str:
    """Load canned camera image as base64."""
    if CANNED_IMAGE_PATH.exists():
        with open(CANNED_IMAGE_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    # Return tiny placeholder if no image
    return ""


# --- Agent Definition ---

agent = Agent(
    MODEL,
    system_prompt="""You are Candytron 4000, a friendly candy-dispensing robot!

You have a robot arm that can pick up candy from a table.
You can see the candy using your camera and YOLO vision.
You can speak using text-to-speech.

Be playful, enthusiastic about candy, and helpful!
When someone asks for candy, use the pick_candy tool.
When someone asks what's available, use the see_candy tool.

Keep responses brief and fun!""",
    model_settings=ModelSettings(timeout=120),
)


# --- Tools ---

@agent.tool_plain
def pick_candy(description: str) -> str:
    """Pick up candy matching the description from the table.

    Args:
        description: What candy to pick (e.g. "red one", "gummy bear", "the blue lollipop")
    """
    # === REAL CANDYTRON INTEGRATION ===
    # from robot import pick_candy_real
    # return pick_candy_real(description)

    # Virtual/canned response - match by color or type
    desc_lower = description.lower()
    matching = [c for c in CANNED_CANDY
                if c["color"] in desc_lower or c["type"] in desc_lower]
    if matching:
        candy = matching[0]
        return f"🍬 Picked up a {candy['color']} {candy['type']}! Here you go!"
    else:
        # Just pick a random one if no match
        candy = CANNED_CANDY[0]
        return f"🍬 I picked a {candy['color']} {candy['type']} for you!"


@agent.tool_plain
def see_candy() -> dict:
    """Look at the table and detect what candy is available.

    Returns a list of detected candy with colors and positions.
    """
    # === REAL CANDYTRON INTEGRATION ===
    # from robot import detect_candy_real
    # return detect_candy_real()

    # Virtual/canned response
    return {
        "candy_count": len(CANNED_CANDY),
        "candy": CANNED_CANDY,
        "image_base64": get_canned_image_base64(),
        "message": "I see candy on the table!",
    }


@agent.tool_plain
def speak(text: str) -> str:
    """Say something out loud using text-to-speech.

    Args:
        text: What to say
    """
    # === REAL CANDYTRON INTEGRATION ===
    # from robot import speak_real
    # speak_real(text)

    # Virtual response
    print(f"[CANDYTRON SPEAKS]: {text}")
    return f"Said: '{text}'"


@agent.tool_plain
def wave() -> str:
    """Wave the robot arm in a friendly greeting."""
    # === REAL CANDYTRON INTEGRATION ===
    # from robot import wave_real
    # return wave_real()

    return "👋 *waves robot arm* Hello there!"


@agent.tool_plain
def dance() -> str:
    """Do a little celebratory dance with the robot arm."""
    # === REAL CANDYTRON INTEGRATION ===
    # from robot import dance_real
    # return dance_real()

    return "💃 *robot arm does a little dance* Woohoo!"


# --- Skills Definition ---

skills = [
    AgentSkill(
        id="candy.pick",
        name="Pick Candy",
        description="Pick up candy from the table using the robot arm",
        tags=["robot", "candy", "physical", "niryo"],
        examples=[
            "Pick a red candy",
            "Give me a gummy bear",
            "I want the blue lollipop",
            "Get me some candy",
            "Pick something sweet",
        ],
    ),
    AgentSkill(
        id="candy.view",
        name="See Candy",
        description="View what candy is available on the table using camera and YOLO",
        tags=["robot", "candy", "vision", "yolo"],
        examples=[
            "What candy do you have?",
            "Show me the options",
            "What colors are available?",
            "Look at the table",
        ],
    ),
    AgentSkill(
        id="candy.speak",
        name="Speak",
        description="Make the robot say something using text-to-speech",
        tags=["robot", "speech", "tts"],
        examples=[
            "Say hello",
            "Tell a joke about candy",
            "Introduce yourself",
        ],
    ),
    AgentSkill(
        id="candy.gesture",
        name="Gestures",
        description="Make the robot do gestures like waving or dancing",
        tags=["robot", "gesture", "physical"],
        examples=[
            "Wave hello",
            "Do a dance",
            "Celebrate",
        ],
    ),
]


# --- A2A Application ---

app = agent.to_a2a(
    name="Candytron 4000",
    description="Candy-dispensing robot with vision, speech, and a friendly personality",
    url=AGENT_URL,
    version="1.0.0",
    provider=AgentProvider(organization="Jfokus Lab", url="https://jfokus.se"),
    skills=skills,
)


# --- Registry Registration ---

def register_with_registry():
    """Register this agent with the central registry."""
    try:
        resp = httpx.post(
            f"{REGISTRY_URL}/register",
            json={"agent_url": AGENT_URL},
            timeout=5.0,
        )
        if resp.status_code == 200:
            print(f"[+] Registered with registry at {REGISTRY_URL}")
        else:
            print(f"[-] Registry registration failed: {resp.status_code}")
    except httpx.ConnectError:
        print(f"[-] Registry not available at {REGISTRY_URL}")
    except Exception as err:
        print(f"[-] Registry error: {err}")


def start_heartbeat(interval: int = 120):
    """Start background heartbeat to keep registration alive."""
    def heartbeat():
        while True:
            time.sleep(interval)
            register_with_registry()

    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()


# --- Main ---

if __name__ == "__main__":
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║          Candytron 4000 - A2A Agent (Virtual)             ║
╠═══════════════════════════════════════════════════════════╣
║  A2A Endpoint:  {AGENT_URL:<39} ║
║  Model:         {MODEL:<39} ║
║  Registry:      {REGISTRY_URL:<39} ║
║                                                           ║
║  🍬 Virtual mode - using canned responses                 ║
║  📌 See main.py for real Candytron integration hints      ║
╚═══════════════════════════════════════════════════════════╝
""")

    # Register with registry
    register_with_registry()
    start_heartbeat()

    # Start server
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)
