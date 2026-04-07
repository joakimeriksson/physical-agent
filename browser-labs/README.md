# Browser Labs

Browser-based labs for the hackathon. No Python, no package manager, no installations needed — just a browser.

## Setup

Serve the files with any static HTTP server:

```bash
cd browser-labs
python -m http.server 8080
```

Then open `http://localhost:8080/` in your browser.

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

## Suggested Order

1. **lab2_chat_agent** — Start here. Chat with AI, see tool calling in action.
2. **lab1_business_coach** — Fun demo with webcam. Needs a vision model (gemma3).
3. **lab3_iot_dashboard** — The main event. Control real IKEA devices!
