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
python serve.py
```

Open <http://localhost:9090/lab2_business_coach/> and enter the Ollama URL + API key in the settings bar.

(`serve.py` serves from `browser-labs/` so the shared `../config.json` is reachable.)
