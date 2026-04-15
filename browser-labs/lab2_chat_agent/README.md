# Lab 2: Chat Agent with Tools

Chat with an LLM that can call three local JavaScript tools: **calculator**, **time**, and **dice roll**. The browser talks directly to Ollama, parses `tool_calls` from the response, runs the tool in JS, and sends the result back in another turn — classic tool-calling loop, no backend.

```
Browser ⇄ Ollama  (with tools=[calc, time, dice])
   ↑         ↓
   └── run tool locally ──┘
```

Try: *"What's 17 * 23 plus the current hour?"* or *"Roll 2d20."*

## Run

```bash
python -m http.server 9090     # or: uv run python -m http.server 9090
```

Open <http://localhost:9090/> and enter the Ollama URL + API key in the settings bar.
