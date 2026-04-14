# Lab 4: Smart Home Agent

A full smart home agent with camera, chat, and IoT control.

```
Browser                          Python Server (localhost:8080)
├── Chat UI                 →    POST /api/chat → Ollama + tool calling → MCP
├── Camera (getUserMedia)   →    POST /api/analyze → Ollama vision
├── Device panel            ←    GET /api/sensors, /api/lights
└── Spoken responses        ←    Browser TTS
                                      ↓
                                 Ollama (LLM)
                                 Dirigera MCP (IoT)
```

## Setup

```bash
cd browser-labs/lab4_full_agent
uv sync
```

Edit `../config.json` with your API keys (copy from `../config.example.json` if needed).

## Run

```bash
uv run python server.py
```

Open http://localhost:8080 in your browser.

## What to try

- "What lights are available?"
- "Turn on Lampa Soffa"
- "What's the temperature?"
- "Set the lamp to 50% brightness"
- Take a photo and ask "Am I ready for a meeting?"

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Chat with IoT tool calling |
| `/api/analyze` | POST | Analyze an image with vision LLM |
| `/api/sensors` | GET | Get all sensor readings |
| `/api/lights` | GET | Get all lights |
| `/api/outlets` | GET | Get all outlets |
| `/api/command` | POST | Execute IoT command |

## Challenges

1. Add a "mood lighting" feature — ask the agent to set the light color based on the room temperature
2. Add speech input using the Web Speech API (browser has `webkitSpeechRecognition`)
3. Make the agent automatically monitor CO2 and warn you when it's too high
