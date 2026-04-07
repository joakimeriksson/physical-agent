# Browser Labs

Browser-based versions of the physical agent labs. These run entirely in the browser — no Python, no package manager, no driver installations needed.

## Prerequisites

- **Ollama** running with CORS enabled:
  ```bash
  OLLAMA_ORIGINS="*" ollama serve
  ```
- A webcam (accessed via browser `getUserMedia`)

## Labs

| Lab | Description | Devices |
|-----|-------------|---------|
| [lab1_business_coach](lab1_business_coach/) | Business Readiness Coach — AI evaluates your meeting readiness | Camera, Ollama VLM, Browser TTS |

## Running

Serve the files with any static HTTP server:

```bash
# Python
cd browser-labs
python -m http.server 8080

# Node
npx serve browser-labs
```

Then open `http://localhost:8080/lab1_business_coach/` in your browser.

> **Note:** Opening `index.html` directly as a `file://` URL won't work because `getUserMedia` requires a secure context (HTTPS or localhost).
