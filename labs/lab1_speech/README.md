# Lab 1: Speech

> **Physical Agent Lab Series**
> AI is moving from the digital world into the physical world. In this lab series, we explore how AI can control real devices - robot arms, smart homes, and more. Speech is the natural interface for humans to communicate with physical agents.

Local speech-to-text and text-to-speech - no cloud APIs needed.

## Components

- **STT:** whisper.cpp (fast C++ implementation)
- **TTS:** Piper (natural neural voices)

## Setup

```bash
pixi install
```

## Usage

```bash
pixi run demo      # Interactive: listen → transcribe → speak
pixi run record    # Record and transcribe only
pixi run tts "Hello world"  # Text-to-speech only
```

## Models

Models are downloaded automatically on first run:
- Whisper `base` (~140MB) - good balance of speed/accuracy
- Piper `en_US-lessac-medium` (~60MB) - natural English voice

## API

```python
from main import listen, speak

# Record from mic and transcribe
text = listen(duration=5.0)

# Speak text
speak("Hello, I heard you say: " + text)
```
