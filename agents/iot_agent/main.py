#!/usr/bin/env python3
"""IoT Agent - A2A Server connecting to DIRIGERA via MCP

Production IoT agent that:
- Connects to real DIRIGERA MCP server for device control
- Exposes capabilities via A2A protocol
- Auto-registers with the agent registry
- Pre-fetches device metadata at startup for faster responses

Usage:
    # Set MCP server URL and run
    DIRIGERA_MCP_URL=http://localhost:8080 pixi run agent

    # Or with all options
    DIRIGERA_MCP_URL=http://dirigera.local:8080 \
    REGISTRY_URL=http://registry:8000 \
    IOT_AGENT_PORT=9998 \
    pixi run agent
"""
import asyncio
import json
import os
import logging
import threading
from datetime import datetime

import httpx
import uvicorn
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP
from a2a.types import AgentProvider

# Enable debug logging for pydantic-ai
DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")
if DEBUG:
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
    logging.getLogger("pydantic_ai").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.DEBUG)
    print("[DEBUG MODE ENABLED]")

# Configuration
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("PYDANTIC_AI_MODEL", "ollama:qwen3:4b")
REGISTRY_URL = os.environ.get("REGISTRY_URL", "http://localhost:8000")
AGENT_PORT = int(os.environ.get("IOT_AGENT_PORT", "9998"))
AGENT_URL = os.environ.get("IOT_AGENT_URL", f"http://localhost:{AGENT_PORT}")
DIRIGERA_MCP_URL = os.environ.get("DIRIGERA_MCP_URL", "")

if not DIRIGERA_MCP_URL:
    print("ERROR: DIRIGERA_MCP_URL environment variable is required")
    print("Example: DIRIGERA_MCP_URL=http://localhost:8080 pixi run agent")
    exit(1)


# --- MCP Connection ---

mcp_server = MCPServerHTTP(url=f"{DIRIGERA_MCP_URL}/sse")


# --- Device Discovery at Startup (using MCP client) ---

# Store full device metadata globally
DEVICE_METADATA = {"lights": [], "sensors": [], "outlets": []}


def discover_devices_sync():
    """Fetch device lists from MCP server at startup using direct MCP client."""
    from mcp import ClientSession
    from mcp.client.sse import sse_client

    devices = {"lights": [], "sensors": [], "outlets": []}
    mcp_url = f"{DIRIGERA_MCP_URL}/sse"

    async def _discover():
        print(f"[*] Connecting to MCP server at {mcp_url}...", flush=True)

        async with sse_client(mcp_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("[+] MCP session initialized", flush=True)

                # Get lights
                try:
                    result = await session.call_tool("get_lights", {})
                    if result and result.content:
                        data = json.loads(result.content[0].text)
                        if isinstance(data, list):
                            devices["lights"] = data
                        elif isinstance(data, dict):
                            devices["lights"] = [data]
                    print(f"[+] Discovered {len(devices['lights'])} lights:")
                    for light in devices["lights"]:
                        name = light.get("name", "?") if isinstance(light, dict) else str(light)
                        print(f"    - {name}")
                except Exception as e:
                    print(f"[-] Failed to get lights: {e}")

                # Get environment sensors
                try:
                    result = await session.call_tool("get_environment_sensors", {})
                    if result and result.content:
                        data = json.loads(result.content[0].text)
                        if isinstance(data, list):
                            devices["sensors"] = data
                    print(f"[+] Discovered {len(devices['sensors'])} sensors:")
                    for sensor in devices["sensors"]:
                        name = sensor.get("name", "?") if isinstance(sensor, dict) else str(sensor)
                        print(f"    - {name}")
                except Exception as e:
                    print(f"[-] Failed to get sensors: {e}")

                # Get outlets
                try:
                    result = await session.call_tool("get_outlets", {})
                    if result and result.content:
                        data = json.loads(result.content[0].text)
                        if isinstance(data, list):
                            devices["outlets"] = data
                    print(f"[+] Discovered {len(devices['outlets'])} outlets:")
                    for outlet in devices["outlets"]:
                        name = outlet.get("name", "?") if isinstance(outlet, dict) else str(outlet)
                        print(f"    - {name}")
                except Exception as e:
                    print(f"[-] Failed to get outlets: {e}")

        return devices

    return asyncio.run(_discover())


def format_device_info(devices: list, device_type: str) -> str:
    """Format device info with metadata for the prompt."""
    if not devices:
        return "none discovered"

    lines = []
    for d in devices:
        if isinstance(d, dict):
            name = d.get("name", "unknown")
            if device_type == "light":
                brightness = d.get("light_level", "?")
                lines.append(f'"{name}" (brightness: {brightness}%)')
            elif device_type == "sensor":
                temp = d.get("temperature", d.get("current_temperature"))
                humidity = d.get("humidity", d.get("current_humidity"))
                info = []
                if temp is not None:
                    info.append(f"temp: {temp}°C")
                if humidity is not None:
                    info.append(f"humidity: {humidity}%")
                extra = f" ({', '.join(info)})" if info else ""
                lines.append(f'"{name}"{extra}')
            elif device_type == "outlet":
                power = d.get("power", d.get("current_power"))
                extra = f" (power: {power}W)" if power else ""
                lines.append(f'"{name}"{extra}')
        else:
            lines.append(f'"{d}"')
    return "\n  ".join(lines)


def build_system_prompt(devices: dict) -> str:
    """Build system prompt with discovered device names and metadata."""
    lights_str = format_device_info(devices.get("lights", []), "light")
    sensors_str = format_device_info(devices.get("sensors", []), "sensor")
    outlets_str = format_device_info(devices.get("outlets", []), "outlet")

    return f"""You are an IoT smart home assistant connected to real IKEA DIRIGERA devices.

AVAILABLE DEVICES:

Lights:
  {lights_str}

Sensors:
  {sensors_str}

Outlets:
  {outlets_str}

CAPABILITIES:
- Lights: turn on/off, set brightness (0-100), set color temperature
- Sensors: read temperature, humidity, CO2, VOC, PM2.5
- Outlets: turn on/off, read power consumption

Use the MCP tools to control devices. Use the EXACT device names listed above (in quotes).
Be helpful and confirm actions taken."""


# Discover devices at module load
import sys
print("[*] Discovering devices from MCP server...", flush=True)
try:
    DISCOVERED_DEVICES = discover_devices_sync()
    DEVICE_METADATA = DISCOVERED_DEVICES.copy()
    print("[+] Device discovery complete!", flush=True)
except Exception as e:
    import traceback
    print(f"[-] Device discovery failed: {e}", flush=True)
    traceback.print_exc()
    DISCOVERED_DEVICES = {"lights": [], "sensors": [], "outlets": []}


# --- Pydantic AI Agent with MCP Tools ---

from pydantic_ai.settings import ModelSettings

agent = Agent(
    MODEL,
    system_prompt=build_system_prompt(DISCOVERED_DEVICES),
    mcp_servers=[mcp_server],
    model_settings=ModelSettings(timeout=120),  # 2 minute timeout for slow models
)


# Additional tools for common queries

@agent.tool_plain
def get_current_time() -> str:
    """Get the current date and time."""
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


@agent.tool_plain
def assess_air_quality(co2: int, voc: int) -> str:
    """Assess air quality based on CO2 and VOC readings.

    Args:
        co2: CO2 level in ppm
        voc: VOC level in ppb
    """
    if co2 < 600 and voc < 100:
        return "Excellent air quality"
    elif co2 < 800 and voc < 200:
        return "Good air quality"
    elif co2 < 1000 and voc < 300:
        return "Moderate - consider ventilation"
    elif co2 < 1500:
        return "Poor - ventilation recommended"
    else:
        return "Very poor - open windows immediately!"


# --- A2A Application with Skills ---

from a2a.types import AgentSkill

# Define IoT skills for discovery
iot_skills = [
    AgentSkill(
        id="iot.light.control",
        name="Light Control",
        description="Control smart lights - turn on/off, adjust brightness (0-100%), set color temperature",
        tags=["smart-home", "lighting", "ikea", "dirigera"],
        examples=[
            "Turn on the lamp",
            "Set the light to 50%",
            "Turn off all lights",
            "Dim the living room light",
        ],
    ),
    AgentSkill(
        id="iot.sensor.environment",
        name="Environment Sensors",
        description="Read environmental sensors - temperature, humidity, CO2 levels, VOC, PM2.5 air quality",
        tags=["smart-home", "sensors", "temperature", "air-quality", "ikea"],
        examples=[
            "What's the temperature?",
            "How's the air quality?",
            "What's the humidity level?",
            "Check the CO2 levels",
        ],
    ),
    AgentSkill(
        id="iot.outlet.control",
        name="Outlet Control",
        description="Control smart outlets - turn on/off, read power consumption (watts, voltage, current)",
        tags=["smart-home", "outlet", "power", "energy", "ikea"],
        examples=[
            "Turn off the ventilation",
            "What's the power usage?",
            "How much power is the office using?",
        ],
    ),
]

app = agent.to_a2a(
    name="IoT Agent",
    description="Smart home control agent connected to IKEA DIRIGERA - lights and environment sensors",
    url=AGENT_URL,
    version="1.0.0",
    provider=AgentProvider(organization="Jfokus Lab", url="https://jfokus.se"),
    skills=iot_skills,
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
    import time

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
║         IoT Agent - DIRIGERA Smart Home Control           ║
╠═══════════════════════════════════════════════════════════╣
║  A2A Endpoint:  {AGENT_URL:<39} ║
║  MCP Server:    {DIRIGERA_MCP_URL:<39} ║
║  Model:         {MODEL:<39} ║
║                                                           ║
║  Connected to real DIRIGERA devices via MCP               ║
╚═══════════════════════════════════════════════════════════╝
""")

    # Register with registry
    register_with_registry()
    start_heartbeat()

    # Start server
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)
