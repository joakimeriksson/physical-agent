# Lab 3: IoT Smart Home Dashboard

Control real IKEA smart home devices with natural language. The browser sends your prompt to Ollama, which decides to call tools exposed by a remote **Dirigera MCP** server — turning lights on/off, dimming, reading sensors, etc.

```
Browser ⇄ Ollama (tool calling)
Browser ⇄ Dirigera MCP ⇄ IKEA hub ⇄ Zigbee devices
```

Try: *"Turn on Lampa Soffa"*, *"Dim all lights to 20%"*, *"What's the temperature?"*

## Run

```bash
python -m http.server 9090     # or: uv run python -m http.server 9090
```

Open <http://localhost:9090/> and fill in both Ollama and MCP URL + API keys in the settings bar.
