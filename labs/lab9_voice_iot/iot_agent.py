#!/usr/bin/env python3
"""IoT Agent - A2A Server for Smart Home Control (Simulated)

This agent exposes IoT control via A2A protocol using pydantic-ai.
Uses simulated devices for the lab exercise.

Usage:
    pixi run iot-agent
"""
import os
import random
from datetime import datetime

import uvicorn
from pydantic_ai import Agent
from a2a.types import AgentProvider

# Configuration
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("PYDANTIC_AI_MODEL", "ollama:qwen3:4b")


# --- Simulated IoT Hub ---

class SimulatedIoTHub:
    """Simulated IoT hub for lab exercise."""

    def __init__(self):
        self.devices = {
            "living_room_light": {"type": "light", "state": "off", "brightness": 0},
            "bedroom_light": {"type": "light", "state": "on", "brightness": 80},
            "kitchen_light": {"type": "light", "state": "off", "brightness": 0},
            "environment": {
                "temperature": 21.5,
                "humidity": 45.0,
                "co2": 650,
                "voc": 120,
            },
        }

    def list_devices(self) -> str:
        lines = ["Available IoT devices:"]
        for name, info in self.devices.items():
            if info.get("type") == "light":
                state = f"{info['state']} (brightness: {info['brightness']}%)"
                lines.append(f"  - {name}: {state}")
        lines.append("  - environment sensors: temp, humidity, CO2, VOC")
        return "\n".join(lines)

    def control_light(self, room: str, action: str) -> str:
        key = f"{room.lower().replace(' ', '_')}_light"
        if key not in self.devices:
            return f"Unknown light: {room}"

        device = self.devices[key]
        if action.lower() in ("on", "turn on"):
            device["state"] = "on"
            device["brightness"] = 100
            return f"Turned on {key}"
        elif action.lower() in ("off", "turn off"):
            device["state"] = "off"
            device["brightness"] = 0
            return f"Turned off {key}"
        elif action.replace("%", "").isdigit():
            brightness = int(action.replace("%", ""))
            device["brightness"] = max(0, min(100, brightness))
            device["state"] = "on" if brightness > 0 else "off"
            return f"Set {key} brightness to {brightness}%"
        return f"Unknown action: {action}"

    def get_environment(self) -> dict:
        env = self.devices["environment"]
        return {
            "temperature": round(env["temperature"] + random.uniform(-0.3, 0.3), 1),
            "humidity": round(env["humidity"] + random.uniform(-1, 1), 1),
            "co2": int(env["co2"] + random.randint(-20, 20)),
            "voc": int(env["voc"] + random.randint(-10, 10)),
        }


hub = SimulatedIoTHub()


# --- Pydantic AI Agent ---

agent = Agent(
    MODEL,
    system_prompt="""You are an IoT smart home assistant. You control lights and read environment sensors.

Available:
- Lights: living room, bedroom, kitchen (on/off, brightness)
- Sensors: temperature, humidity, CO2, VOC

Be helpful and confirm what you did.""",
)


@agent.tool_plain
def list_devices() -> str:
    """List all available IoT devices."""
    return hub.list_devices()


@agent.tool_plain
def control_light(room: str, action: str) -> str:
    """Control a light. Room: living_room, bedroom, kitchen. Action: on, off, or percentage."""
    return hub.control_light(room, action)


@agent.tool_plain
def get_temperature() -> str:
    """Get current room temperature."""
    env = hub.get_environment()
    return f"Temperature: {env['temperature']}°C"


@agent.tool_plain
def get_humidity() -> str:
    """Get current room humidity."""
    env = hub.get_environment()
    return f"Humidity: {env['humidity']}%"


@agent.tool_plain
def get_co2_level() -> str:
    """Get current CO2 level."""
    env = hub.get_environment()
    return f"CO2: {env['co2']} ppm"


@agent.tool_plain
def get_voc_level() -> str:
    """Get current VOC level."""
    env = hub.get_environment()
    return f"VOC: {env['voc']} ppb"


@agent.tool_plain
def get_environment_report() -> str:
    """Get full environment report."""
    env = hub.get_environment()
    co2 = env["co2"]
    quality = "Good" if co2 < 800 else "Moderate" if co2 < 1000 else "Poor"
    return f"""Environment:
  Temperature: {env['temperature']}°C
  Humidity: {env['humidity']}%
  CO2: {co2} ppm
  VOC: {env['voc']} ppb
  Air Quality: {quality}"""


@agent.tool_plain
def get_current_time() -> str:
    """Get current date and time."""
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


# --- A2A Application ---

app = agent.to_a2a(
    name="IoT Agent",
    description="Smart home control - lights and environment sensors (simulated)",
    url="http://localhost:9998",
    version="1.0.0",
    provider=AgentProvider(organization="Jfokus Lab", url="https://jfokus.se"),
)


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║           IoT Agent - Smart Home Control                  ║
╠═══════════════════════════════════════════════════════════╣
║  A2A Endpoint: http://localhost:9998                      ║
║  Devices: lights (3), environment sensors                 ║
║                                                           ║
║  This is a SIMULATED hub for the lab exercise.            ║
║  Run 'pixi run demo' for voice control.                   ║
╚═══════════════════════════════════════════════════════════╝
""")
    uvicorn.run(app, host="0.0.0.0", port=9998)
