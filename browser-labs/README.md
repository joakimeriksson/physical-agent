# Browser Labs

Browser-based labs for the hackathon. No Python, no package manager, no installations needed — just a browser.

## Setup

Serve the files with any static HTTP server. You can either serve the whole `browser-labs/` folder:

```bash
cd browser-labs
python -m http.server 9090        # or: uv run python -m http.server 9090
```

…or just the single lab you're working on:

```bash
cd browser-labs/lab2_chat_agent
python -m http.server 9090        # or: uv run python -m http.server 9090
```

Then open `http://localhost:9090/` in your browser. Lab 4 is different — it ships its own Python server started with `uv run python server.py` (see below).

> **Note:** Opening `index.html` directly as a `file://` URL won't work because `getUserMedia` requires a secure context (HTTPS or localhost).

## Configuration

All labs have a settings bar where you enter:
- **Ollama URL**: `https://ollama.botbox.se` (provided by instructor)
- **API Key**: Shared key shown on projector

The IoT dashboard also needs:
- **MCP Server URL**: `https://dirigera.botbox.se`
- **MCP API Key**: Shown on projector

## Labs

| Lab | Description | Requires |
|-----|-------------|----------|
| [lab1_business_coach](lab1_business_coach/) | AI evaluates your meeting readiness | Webcam, Ollama VLM |
| [lab2_chat_agent](lab2_chat_agent/) | Chat with an AI that calls tools (calculator, time, dice) | Ollama |
| [lab3_iot_dashboard](lab3_iot_dashboard/) | Control IKEA smart home devices with natural language | Ollama + Dirigera MCP |
| [lab4_full_agent](lab4_full_agent/) | Capstone: vision + chat + MCP + voice in one agent | Webcam, Ollama, Dirigera MCP, `uv` |

## Suggested Order

1. **lab2_chat_agent** — Start here. Chat with AI, see tool calling in action.
2. **lab1_business_coach** — Fun demo with webcam. Needs a vision model (gemma3).
3. **lab3_iot_dashboard** — Control real IKEA devices!
4. **lab4_full_agent** — The capstone. Everything combined into one smart-home agent.
