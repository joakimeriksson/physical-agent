# Lab 1: Business Readiness Coach

A webcam snapshot is sent to a vision LLM (Ollama VLM, e.g. `gemma3`) which scores your clothing, grooming, background, and pose — telling you whether you're ready for that Teams call.

```
Browser: getUserMedia → <canvas> → base64 JPEG
       → POST /api/chat (Ollama, vision model)
       → verdict rendered in UI
```

Everything runs in the browser — no backend needed.

## Run

```bash
python -m http.server 9090     # or: uv run python -m http.server 9090
```

Open <http://localhost:9090/> and enter the Ollama URL + API key in the settings bar.
