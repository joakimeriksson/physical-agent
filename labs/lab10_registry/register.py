#!/usr/bin/env python3
"""Simple agent registration helper.

Import this in your agent to register with the central registry.

Usage:
    from register import register, register_with_heartbeat

    # One-time registration
    register("http://registry:8000", "http://my-agent:9999")

    # With heartbeat (re-registers every 60s)
    register_with_heartbeat("http://registry:8000", "http://my-agent:9999")
"""
import os
import threading
import time
from typing import Optional

import httpx


def register(
    registry_url: str,
    agent_url: str,
    name: Optional[str] = None,
    timeout: float = 10.0,
) -> bool:
    """Register agent with the central registry.

    Args:
        registry_url: URL of the registry (e.g., http://192.168.1.100:8000)
        agent_url: URL of your agent (e.g., http://192.168.1.50:9999)
        name: Optional name override
        timeout: Request timeout

    Returns:
        True if registration succeeded
    """
    try:
        resp = httpx.post(
            f"{registry_url.rstrip('/')}/register",
            json={"agent_url": agent_url, "name": name},
            timeout=timeout,
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"[Registry] Registered as '{data.get('name')}' at {data.get('url')}")
            return True
        print(f"[Registry] Registration failed: {resp.status_code} {resp.text}")
        return False
    except Exception as err:
        print(f"[Registry] Registration error: {err}")
        return False


def unregister(registry_url: str, agent_url: str) -> bool:
    """Unregister agent from the registry."""
    try:
        resp = httpx.delete(
            f"{registry_url.rstrip('/')}/agents/{agent_url}",
            timeout=10.0,
        )
        return resp.status_code == 200
    except Exception:
        return False


def register_with_heartbeat(
    registry_url: str,
    agent_url: str,
    name: Optional[str] = None,
    interval: int = 60,
) -> threading.Thread:
    """Register and keep re-registering every interval seconds.

    Args:
        registry_url: URL of the registry
        agent_url: URL of your agent
        name: Optional name override
        interval: Seconds between heartbeats (default: 60)

    Returns:
        The heartbeat thread (daemon, auto-stops with main program)
    """
    def heartbeat():
        while True:
            register(registry_url, agent_url, name)
            time.sleep(interval)

    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()
    print(f"[Registry] Heartbeat started (every {interval}s)")
    return thread


# Environment-based auto-registration
REGISTRY_URL = os.environ.get("A2A_REGISTRY_URL")
AGENT_URL = os.environ.get("A2A_AGENT_URL")


def auto_register(agent_url: Optional[str] = None, name: Optional[str] = None):
    """Auto-register if A2A_REGISTRY_URL is set.

    Args:
        agent_url: Agent URL (or uses A2A_AGENT_URL env var)
        name: Optional name override
    """
    if not REGISTRY_URL:
        return None

    url = agent_url or AGENT_URL
    if not url:
        print("[Registry] Set A2A_AGENT_URL to auto-register")
        return None

    return register_with_heartbeat(REGISTRY_URL, url, name)


# --- CLI ---

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python register.py <registry_url> <agent_url>")
        print("Example: python register.py http://192.168.1.100:8000 http://192.168.1.50:9999")
        sys.exit(1)

    registry = sys.argv[1]
    agent = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else None

    if register(registry, agent, name):
        print("Success!")
    else:
        print("Failed!")
        sys.exit(1)
