# Lab 10: Agent Registry

> **Physical Agent Lab Series**
> A shared registry where all participants can register and discover each other's agents.

## Overview

```
┌─────────────────┐     register      ┌─────────────────┐
│  Your Agent     │ ────────────────→ │    Registry     │
│  192.168.1.50   │                   │  192.168.1.100  │
└─────────────────┘                   │     :8000       │
                                      │                 │
┌─────────────────┐     register      │  ┌───────────┐  │
│  Team 2 Agent   │ ────────────────→ │  │  Agent 1  │  │
│  192.168.1.51   │                   │  │  Agent 2  │  │
└─────────────────┘                   │  │  Agent 3  │  │
                                      │  │    ...    │  │
┌─────────────────┐     register      │  └───────────┘  │
│  Team 3 Agent   │ ────────────────→ │                 │
│  192.168.1.52   │                   │   Web UI 📺     │
└─────────────────┘                   └─────────────────┘
```

## For the Instructor

### Start the Registry (Central Machine)

```bash
cd labs/lab10_registry
pixi install
pixi run registry
```

The registry will display:
- **Web UI**: `http://<your-ip>:8000` (show on big screen!)
- **API**: `http://<your-ip>:8000/agents`

Tell participants: **"Register your agents at `http://192.168.1.100:8000`"**

---

## For Participants

### Option 1: Register via Command Line

```bash
curl -X POST "http://<registry-ip>:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"agent_url": "http://<your-ip>:9999"}'
```

### Option 2: Add to Your Agent Code

Copy `register.py` to your lab folder, then:

```python
from register import register_with_heartbeat

# At startup, after your server is running
register_with_heartbeat(
    registry_url="http://192.168.1.100:8000",
    agent_url="http://192.168.1.50:9999",  # Your IP!
)
```

### Option 3: Environment Variables

```bash
export A2A_REGISTRY_URL="http://192.168.1.100:8000"
export A2A_AGENT_URL="http://192.168.1.50:9999"
```

Then in your agent:
```python
from register import auto_register
auto_register()
```

---

## Example: Add Registration to Lab 8

Edit `lab8_a2a/agent_b.py`:

```python
# Add at the top
import sys
sys.path.insert(0, "../lab10_registry")
from register import register_with_heartbeat

# Add after uvicorn.run starts (or in a separate thread before)
register_with_heartbeat(
    registry_url="http://192.168.1.100:8000",
    agent_url="http://192.168.1.50:9999",
)
```

---

## API Reference

### Register an Agent
```bash
POST /register
Content-Type: application/json

{"agent_url": "http://your-ip:9999"}
# or
{"card_url": "http://your-ip:9999/.well-known/agent-card.json"}
# optionally
{"agent_url": "...", "name": "My Cool Agent"}
```

### List All Agents
```bash
GET /agents

# Response:
{
  "agents": [
    {
      "name": "Tool Agent",
      "description": "An agent with calculator...",
      "url": "http://192.168.1.50:9999",
      "skills": ["Calculator & Time"],
      "last_seen": "2026-01-27T14:30:00"
    }
  ]
}
```

### A2A-Compatible Index
```bash
GET /.well-known/agents/index.json
```

### Unregister
```bash
DELETE /agents/{agent_url}
```

---

## Features

- **Auto-refresh UI**: Updates every 5 seconds
- **Heartbeat support**: Agents re-register to stay active
- **Auto-cleanup**: Removes agents not seen in 5 minutes
- **A2A compatible**: Serves `/.well-known/agents/index.json`

---

## Troubleshooting

**Can't connect to registry?**
- Check firewall: `sudo ufw allow 8000/tcp`
- Verify IP: `hostname -I` or `ipconfig getifaddr en0`

**Agent not showing up?**
- Ensure your agent's `/.well-known/agent-card.json` is accessible
- Check the registry logs for errors

**Agent disappears after a few minutes?**
- Use `register_with_heartbeat()` instead of one-time `register()`
