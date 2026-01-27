#!/usr/bin/env python3
"""IoT Agent - A2A Server for Smart Home Control

This agent exposes IoT control via A2A protocol.
In a real setup, this would connect to DIRIGERA or similar IoT hub.

Usage:
    pixi run iot-agent
"""
import random
from datetime import datetime

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill
from a2a.utils import new_agent_text_message


class SimulatedIoTHub:
    """Simulated IoT hub for demo purposes.

    In production, this would connect to DIRIGERA or similar.
    """

    def __init__(self):
        # Simulated device states
        self.devices = {
            "living_room_light": {"type": "light", "state": "off", "brightness": 0},
            "bedroom_light": {"type": "light", "state": "on", "brightness": 80},
            "kitchen_light": {"type": "light", "state": "off", "brightness": 0},
            "hallway_sensor": {"type": "motion_sensor", "triggered": False},
            "living_room_temp": {"type": "temperature_sensor", "value": 21.5},
            "bedroom_blinds": {"type": "blinds", "position": 100},  # 100 = open
        }

    def list_devices(self) -> str:
        """List all available devices."""
        lines = ["Available IoT devices:"]
        for name, info in self.devices.items():
            device_type = info["type"]
            if device_type == "light":
                state = f"{info['state']} (brightness: {info['brightness']}%)"
            elif device_type == "temperature_sensor":
                state = f"{info['value']}C"
            elif device_type == "motion_sensor":
                state = "motion detected" if info["triggered"] else "no motion"
            elif device_type == "blinds":
                state = f"{info['position']}% open"
            else:
                state = str(info)
            lines.append(f"  - {name} ({device_type}): {state}")
        return "\n".join(lines)

    def control_light(self, device: str, action: str) -> str:
        """Control a light device."""
        device_key = device.lower().replace(" ", "_")
        if not device_key.endswith("_light"):
            device_key = f"{device_key}_light"

        if device_key not in self.devices:
            return f"Unknown device: {device}. Use 'list devices' to see available devices."

        device_info = self.devices[device_key]
        if device_info["type"] != "light":
            return f"{device} is not a light, it's a {device_info['type']}"

        action_lower = action.lower()
        if action_lower in ("on", "turn on"):
            device_info["state"] = "on"
            device_info["brightness"] = 100
            return f"Turned on {device_key}"
        if action_lower in ("off", "turn off"):
            device_info["state"] = "off"
            device_info["brightness"] = 0
            return f"Turned off {device_key}"
        if action_lower.isdigit() or action_lower.endswith("%"):
            brightness = int(action_lower.rstrip("%"))
            device_info["brightness"] = max(0, min(100, brightness))
            device_info["state"] = "on" if brightness > 0 else "off"
            return f"Set {device_key} brightness to {brightness}%"

        return f"Unknown action: {action}. Try 'on', 'off', or a brightness percentage."

    def get_temperature(self) -> str:
        """Get temperature reading."""
        # Simulate slight variation
        temp = self.devices["living_room_temp"]["value"]
        temp += random.uniform(-0.5, 0.5)
        return f"Current temperature: {temp:.1f}C"

    def control_blinds(self, position: int) -> str:
        """Control blinds position."""
        position = max(0, min(100, position))
        self.devices["bedroom_blinds"]["position"] = position
        if position == 0:
            return "Blinds closed"
        if position == 100:
            return "Blinds fully open"
        return f"Blinds set to {position}% open"


class IoTAgent:  # pylint: disable=too-few-public-methods
    """Agent that controls IoT devices."""

    def __init__(self):
        self.hub = SimulatedIoTHub()

    def _handle_blinds(self, msg_lower: str) -> str | None:
        """Handle blinds control commands."""
        if "close" in msg_lower:
            return self.hub.control_blinds(0)
        if "open" in msg_lower:
            return self.hub.control_blinds(100)
        for word in msg_lower.split():
            if word.isdigit():
                return self.hub.control_blinds(int(word))
        return None

    def _handle_light(self, msg_lower: str) -> str | None:
        """Handle light control commands."""
        room = "living_room"
        for r in ["living room", "bedroom", "kitchen"]:
            if r in msg_lower:
                room = r.replace(" ", "_")
                break

        if any(word in msg_lower for word in ["on", "turn on", "switch on"]):
            return self.hub.control_light(room, "on")
        if any(word in msg_lower for word in ["off", "turn off", "switch off"]):
            return self.hub.control_light(room, "off")

        for word in msg_lower.split():
            if word.isdigit() or word.rstrip("%").isdigit():
                return self.hub.control_light(room, word)
        return None

    async def invoke(self, message: str) -> str:
        """Process a message and control IoT devices."""
        msg_lower = message.lower()

        # List devices
        if any(phrase in msg_lower for phrase in ["list", "devices", "what devices", "show"]):
            return self.hub.list_devices()

        # Temperature
        if any(word in msg_lower for word in ["temperature", "temp", "how warm", "how cold"]):
            return self.hub.get_temperature()

        # Blinds control
        if "blind" in msg_lower:
            result = self._handle_blinds(msg_lower)
            if result:
                return result

        # Light control
        if "light" in msg_lower:
            result = self._handle_light(msg_lower)
            if result:
                return result

        # Time (bonus feature)
        if any(word in msg_lower for word in ["time", "clock"]):
            return f"Current time: {datetime.now().strftime('%H:%M:%S')}"

        # Help
        return (
            "I can control your smart home! Try:\n"
            "  - 'List devices'\n"
            "  - 'Turn on living room light'\n"
            "  - 'Set bedroom light to 50%'\n"
            "  - 'What's the temperature?'\n"
            "  - 'Open/close the blinds'"
        )


class IoTAgentExecutor(AgentExecutor):
    """Executor for IoT A2A requests."""

    def __init__(self):
        self.agent = IoTAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute the IoT agent."""
        # Extract message text
        user_message = ""
        for part in context.message.parts:
            if hasattr(part, "text"):
                user_message = part.text
                break

        result = await self.agent.invoke(user_message)
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Cancel not supported."""
        raise NotImplementedError("cancel not supported")


def main():
    """Start the IoT A2A server."""
    skill = AgentSkill(
        id="iot-control",
        name="Smart Home Control",
        description="Control IKEA smart home devices - lights, sensors, blinds",
        tags=["iot", "smart-home", "lights", "sensors"],
        examples=[
            "Turn on the living room light",
            "What's the temperature?",
            "List all devices",
            "Close the blinds",
        ],
    )

    agent_card = AgentCard(
        name="IoT Agent",
        description="Smart home control agent for IKEA DIRIGERA devices",
        url="http://localhost:9998",
        skills=[skill],
        version="1.0.0",
    )

    handler = DefaultRequestHandler(
        agent_executor=IoTAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    app = A2AStarletteApplication(agent_card=agent_card, http_handler=handler)

    print("Starting IoT Agent (A2A Server) on port 9998...")
    print("Available skills:", [s.name for s in agent_card.skills])
    print("\nThis is a simulated IoT hub for demo purposes.")
    print("In production, connect to a real DIRIGERA hub.\n")
    print("Run 'pixi run demo' in another terminal for voice control.\n")

    uvicorn.run(app.build(), host="0.0.0.0", port=9998)


if __name__ == "__main__":
    main()
