#!/usr/bin/env python3
"""Lab 1: Speech-to-Text and Text-to-Speech

Uses whisper.cpp (fast STT) and Piper (natural TTS) - fully local.

Usage:
    pixi run tts          # Test text-to-speech
    pixi run record       # Record and transcribe
    pixi run demo         # Interactive loop
    pixi run voices       # List available voices
    pixi run devices      # List audio devices (troubleshooting)
    pixi run download-models  # Pre-download models

Linux troubleshooting:
    If you get PortAudio errors, try:
    1. Install system deps: sudo apt install portaudio19-dev libasound2-dev
    2. Check devices: pixi run devices
    3. Set device: export SD_DEVICE=<device_id>
"""

import os
import sys
import wave
from pathlib import Path

import numpy as np

# Try to import sounddevice with helpful error message
try:
    import sounddevice as sd
except OSError as e:
    print(f"Error loading audio library: {e}")
    print("\nLinux fix: sudo apt install portaudio19-dev libasound2-dev")
    print("Then: pixi install --force")
    sys.exit(1)

# Shared models directory (project root)
MODEL_DIR = Path(__file__).parent.parent.parent / "models"

# --- Whisper.cpp STT ---

_whisper_model = None


def download_whisper_model(model: str = "base"):
    """Download whisper.cpp model if not present."""
    from pywhispercpp.utils import download_model as dl
    MODEL_DIR.mkdir(exist_ok=True)
    model_path = MODEL_DIR / f"ggml-{model}.bin"
    if not model_path.exists():
        print(f"Downloading Whisper model '{model}'...")
        dl(model, MODEL_DIR)
    return model_path


def _get_whisper(model: str = "base"):
    """Load whisper.cpp model (cached)."""
    global _whisper_model
    if _whisper_model is None:
        from pywhispercpp.model import Model
        model_path = download_whisper_model(model)
        print("Loading whisper.cpp...")
        _whisper_model = Model(str(model_path))
    return _whisper_model


def list_audio_devices():
    """List available audio devices for troubleshooting."""
    print("Audio Devices:")
    print("-" * 60)
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        kind = []
        if dev["max_input_channels"] > 0:
            kind.append("IN")
        if dev["max_output_channels"] > 0:
            kind.append("OUT")
        marker = " <-- default" if i == sd.default.device[0] or i == sd.default.device[1] else ""
        rate = int(dev.get("default_samplerate", 0))
        print(f"  [{i}] {dev['name']} ({'/'.join(kind)}) {rate}Hz{marker}")
    print("-" * 60)
    print(f"Default input:  {sd.default.device[0]}")
    print(f"Default output: {sd.default.device[1]}")
    print("\nTo use a specific device: export SD_DEVICE=<id>")


def _resample(audio: np.ndarray, orig_rate: int, target_rate: int) -> np.ndarray:
    """Simple linear resampling."""
    if orig_rate == target_rate:
        return audio
    duration = len(audio) / orig_rate
    target_len = int(duration * target_rate)
    indices = np.linspace(0, len(audio) - 1, target_len)
    return np.interp(indices, np.arange(len(audio)), audio).astype(np.float32)


def listen(duration: float = 5.0, model: str = "base") -> str:
    """Record from mic and transcribe with whisper.cpp."""
    # Allow device override via environment
    device = os.environ.get("SD_DEVICE")
    if device:
        device = int(device)
        print(f"Using audio device: {device}")

    # Whisper needs 16kHz, but some devices don't support it
    target_rate = 16000

    # Get device's native sample rate
    dev_info = sd.query_devices(device, "input")
    native_rate = int(dev_info["default_samplerate"])

    # Try 16kHz first, fall back to native rate
    try:
        print(f"Recording {duration}s at {target_rate}Hz...")
        audio = sd.rec(
            int(duration * target_rate),
            samplerate=target_rate,
            channels=1,
            dtype=np.float32,
            device=device,
        )
        sd.wait()
        sample_rate = target_rate
    except Exception as e:
        if "sample rate" in str(e).lower() or "invalid" in str(e).lower():
            print(f"Device doesn't support {target_rate}Hz, using {native_rate}Hz...")
            audio = sd.rec(
                int(duration * native_rate),
                samplerate=native_rate,
                channels=1,
                dtype=np.float32,
                device=device,
            )
            sd.wait()
            sample_rate = native_rate
        else:
            print(f"\nAudio recording failed: {e}")
            print("\nTroubleshooting:")
            print("  1. Run: pixi run devices")
            print("  2. Set device: export SD_DEVICE=<device_id>")
            print("  3. Linux: sudo apt install portaudio19-dev libasound2-dev")
            raise

    # Resample to 16kHz if needed (Whisper requirement)
    audio = audio.flatten()
    if sample_rate != target_rate:
        print(f"Resampling {sample_rate}Hz -> {target_rate}Hz...")
        audio = _resample(audio, sample_rate, target_rate)

    print("Transcribing...")

    whisper = _get_whisper(model)
    segments = whisper.transcribe(audio.flatten())
    text = " ".join(seg.text for seg in segments)
    return text.strip()


# --- Piper TTS ---

_piper_voice = None
PIPER_VOICE = "en_US-lessac-medium"  # Natural American English voice


def download_piper_voice(voice: str = PIPER_VOICE):
    """Download Piper voice model if not present."""
    voice_dir = MODEL_DIR / "piper"
    voice_dir.mkdir(parents=True, exist_ok=True)

    onnx_path = voice_dir / f"{voice}.onnx"
    json_path = voice_dir / f"{voice}.onnx.json"

    if not onnx_path.exists():
        print(f"Downloading Piper voice '{voice}'...")
        base_url = (
            "https://huggingface.co/rhasspy/piper-voices/resolve/main"
            "/en/en_US/lessac/medium"
        )
        import urllib.request  # pylint: disable=import-outside-toplevel
        urllib.request.urlretrieve(f"{base_url}/en_US-lessac-medium.onnx", onnx_path)
        urllib.request.urlretrieve(
            f"{base_url}/en_US-lessac-medium.onnx.json", json_path
        )
        print("Voice downloaded.")

    return onnx_path


def _get_piper():
    """Load Piper voice (cached)."""
    global _piper_voice
    if _piper_voice is None:
        from piper import PiperVoice
        model_path = download_piper_voice()
        print("Loading Piper TTS...")
        _piper_voice = PiperVoice.load(str(model_path))
    return _piper_voice


def speak(text: str):
    """Speak using Piper TTS."""
    voice = _get_piper()

    # Generate audio chunks and combine
    audio_arrays = []
    for chunk in voice.synthesize(text):
        audio_arrays.append(chunk.audio_float_array)

    # Combine and play
    audio = np.concatenate(audio_arrays) if audio_arrays else np.array([])
    sd.play(audio, samplerate=voice.config.sample_rate)
    sd.wait()


def speak_to_file(text: str, path: Path):
    """Save speech to WAV file."""
    voice = _get_piper()

    audio_arrays = []
    for chunk in voice.synthesize(text):
        audio_arrays.append(chunk.audio_float_array)

    audio = np.concatenate(audio_arrays) if audio_arrays else np.array([])
    audio_int16 = (audio * 32767).astype(np.int16)

    # pylint: disable=no-member  # wave.open("wb") returns Wave_write
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(voice.config.sample_rate)
        wav.writeframes(audio_int16.tobytes())


# --- Main ---

def download_models():
    """Pre-download all models."""
    print("Downloading models...")
    download_whisper_model()
    download_piper_voice()
    print("Done!")


def main():
    """Main entry point for speech lab CLI."""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "tts":
        text = " ".join(sys.argv[2:]) or "Hello, I am ready to assist you."
        speak(text)

    elif cmd == "record":
        duration = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
        text = listen(duration)
        print(f"You said: {text}")

    elif cmd == "loop":
        print("Interactive loop. Ctrl+C to exit.\n")
        # Pre-load models
        _get_whisper()
        _get_piper()
        print("Ready!\n")

        while True:
            try:
                text = listen()
                if text:
                    print(f"You: {text}")
                    speak(f"You said: {text}")
            except KeyboardInterrupt:
                print("\nBye!")
                break

    elif cmd == "voices":
        print("Available Piper voices: https://rhasspy.github.io/piper-samples/")
        print(f"Current: {PIPER_VOICE}")

    elif cmd == "devices":
        list_audio_devices()

    elif cmd == "download":
        download_models()

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
