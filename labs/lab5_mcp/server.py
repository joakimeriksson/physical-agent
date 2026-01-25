#!/usr/bin/env python3
"""Simple MCP Server using FastMCP.

Usage:
    pixi run server
"""

import math
import platform
from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("lab5-tools")


@mcp.tool()
def get_time() -> str:
    """Get current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S (%A)")


@mcp.tool()
def get_system_info() -> str:
    """Get system information (OS, platform, Python version)."""
    info = {
        "os": platform.system(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "hostname": platform.node(),
    }
    return "\n".join(f"{k}: {v}" for k, v in info.items())


@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluate a math expression like '2 + 2' or 'sqrt(16)'."""
    allowed = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
        "pi": math.pi, "e": math.e,
    }
    # pylint: disable=eval-used  # Safe: restricted builtins
    return str(eval(expression, {"__builtins__": {}}, allowed))




if __name__ == "__main__":
    mcp.run()
