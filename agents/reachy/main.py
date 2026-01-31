#!/usr/bin/env python3
"""Reachy Mini - Local Conversation Agent

An expressive robot head with voice conversation using Reachy's mic & speaker.
Fully local: Whisper (STT) + Ollama (LLM) + Piper (TTS) + Reachy SDK.

=== HARDWARE INTEGRATION ===

Uses Reachy Mini's built-in audio:
- 4 microphones (wireless) / 2 (lite)
- 5W speaker

SDK audio API:
- mini.microphones.record(duration) - Record from mic
- mini.speaker.say(text) - TTS (if available)
- mini.speaker.play_sound(file) - Play WAV
- mini.media.push_audio_sample(samples) - Low-level audio

See: https://github.com/pollen-robotics/reachy_mini

Usage:
    pixi run agent     # A2A server mode
    pixi run voice     # Voice conversation mode (uses Reachy mic/speaker)
"""

import os
import sys
import time
import threading
from pathlib import Path

import httpx
import uvicorn
import numpy as np
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from a2a.types import AgentSkill, AgentProvider

# --- Configuration ---

os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("PYDANTIC_AI_MODEL", "ollama:qwen2.5:7b")
REGISTRY_URL = os.environ.get("REGISTRY_URL", "http://localhost:8000")
AGENT_PORT = int(os.environ.get("REACHY_PORT", "9997"))
AGENT_URL = os.environ.get("REACHY_URL", f"http://localhost:{AGENT_PORT}")

# Virtual mode flag - set to False when real hardware connected
VIRTUAL_MODE = os.environ.get("REACHY_VIRTUAL", "true").lower() == "true"

# Shared models directory for Whisper/Piper
MODEL_DIR = Path(__file__).parent.parent.parent / "models"


# === SPEECH PIPELINE (Local) ===

_whisper_model = None
_piper_voice = None


def _get_whisper():
    """Load Whisper model for STT."""
    global _whisper_model
    if _whisper_model is None:
        from pywhispercpp.model import Model
        model_path = MODEL_DIR / "ggml-base.bin"
        if not model_path.exists():
            from pywhispercpp.utils import download_model
            MODEL_DIR.mkdir(exist_ok=True)
            download_model("base", MODEL_DIR)
        print("[*] Loading Whisper...")
        _whisper_model = Model(str(model_path))
    return _whisper_model


def _get_piper():
    """Load Piper voice for TTS."""
    global _piper_voice
    if _piper_voice is None:
        from piper import PiperVoice
        voice_dir = MODEL_DIR / "piper"
        onnx_path = voice_dir / "en_US-lessac-medium.onnx"
        if not onnx_path.exists():
            import urllib.request
            voice_dir.mkdir(parents=True, exist_ok=True)
            base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium"
            print("[*] Downloading Piper voice...")
            urllib.request.urlretrieve(f"{base_url}/en_US-lessac-medium.onnx", onnx_path)
            urllib.request.urlretrieve(f"{base_url}/en_US-lessac-medium.onnx.json", f"{onnx_path}.json")
        print("[*] Loading Piper TTS...")
        _piper_voice = PiperVoice.load(str(onnx_path))
    return _piper_voice


def transcribe_audio(audio: np.ndarray, sample_rate: int = 16000) -> str:
    """Transcribe audio using Whisper."""
    # Resample to 16kHz if needed
    if sample_rate != 16000:
        duration = len(audio) / sample_rate
        target_len = int(duration * 16000)
        indices = np.linspace(0, len(audio) - 1, target_len)
        audio = np.interp(indices, np.arange(len(audio)), audio).astype(np.float32)

    whisper = _get_whisper()
    segments = whisper.transcribe(audio.flatten())
    return " ".join(seg.text for seg in segments).strip()


def generate_tts(text: str) -> tuple[np.ndarray, int]:
    """Generate TTS audio using Piper. Returns (audio_array, sample_rate)."""
    voice = _get_piper()
    audio_arrays = []
    for chunk in voice.synthesize(text):
        audio_arrays.append(chunk.audio_float_array)
    audio = np.concatenate(audio_arrays) if audio_arrays else np.array([])
    return audio, voice.config.sample_rate


# === REACHY HARDWARE INTERFACE ===

class ReachyInterface:
    """Interface to Reachy Mini - virtual or real."""

    def __init__(self, virtual: bool = True):
        self.virtual = virtual
        self._mini = None

    def connect(self):
        """Connect to Reachy Mini."""
        if self.virtual:
            print("[*] Virtual mode - no hardware connected")
            return

        # === REAL HARDWARE ===
        # from reachy_mini import ReachyMini
        # self._mini = ReachyMini(media_backend="default")
        # print("[+] Connected to Reachy Mini")

    def disconnect(self):
        """Disconnect from Reachy Mini."""
        if self._mini:
            # self._mini.close()
            pass

    def record_audio(self, duration: float = 5.0) -> tuple[np.ndarray, int]:
        """Record audio from Reachy's microphone."""
        if self.virtual:
            print(f"[VIRTUAL] Recording {duration}s from mic...")
            # Return silence in virtual mode
            sample_rate = 16000
            return np.zeros(int(duration * sample_rate), dtype=np.float32), sample_rate

        # === REAL HARDWARE ===
        # audio = self._mini.microphones.record(duration=duration)
        # sample_rate = self._mini.media.get_input_audio_samplerate()
        # return audio, sample_rate
        return np.zeros(int(duration * 16000), dtype=np.float32), 16000

    def play_audio(self, audio: np.ndarray, sample_rate: int):
        """Play audio through Reachy's speaker."""
        if self.virtual:
            duration = len(audio) / sample_rate
            print(f"[VIRTUAL] Playing {duration:.1f}s audio on speaker...")
            time.sleep(duration * 0.1)  # Simulate some playback time
            return

        # === REAL HARDWARE ===
        # Resample to speaker's sample rate if needed
        # target_rate = self._mini.media.get_output_audio_samplerate()
        # if sample_rate != target_rate:
        #     duration = len(audio) / sample_rate
        #     target_len = int(duration * target_rate)
        #     indices = np.linspace(0, len(audio) - 1, target_len)
        #     audio = np.interp(indices, np.arange(len(audio)), audio).astype(np.float32)
        #
        # # Convert to int16 for speaker
        # audio_int16 = (audio * 32767).astype(np.int16)
        # self._mini.media.push_audio_sample(audio_int16)
        #
        # # Wait for playback
        # time.sleep(len(audio) / target_rate)

    def look_at(self, direction: str) -> str:
        """Move head to look in direction."""
        if self.virtual:
            print(f"[VIRTUAL] Looking {direction}")
            return f"Looking {direction}"

        # === REAL HARDWARE ===
        # from reachy_mini.utils import create_head_pose
        # poses = {
        #     "left": create_head_pose(yaw=30, degrees=True),
        #     "right": create_head_pose(yaw=-30, degrees=True),
        #     "up": create_head_pose(pitch=20, degrees=True),
        #     "down": create_head_pose(pitch=-20, degrees=True),
        #     "center": create_head_pose(),
        # }
        # self._mini.goto_target(head=poses.get(direction, poses["center"]), duration=0.5)
        return f"Looking {direction}"

    def express(self, emotion: str) -> str:
        """Show an emotion through head movement."""
        if self.virtual:
            print(f"[VIRTUAL] Expressing {emotion}")
            return f"*{emotion} expression*"

        # === REAL HARDWARE ===
        # from reachy_mini.utils import create_head_pose
        # expressions = {
        #     "happy": create_head_pose(pitch=5, roll=5, degrees=True),
        #     "sad": create_head_pose(pitch=-15, degrees=True),
        #     "curious": create_head_pose(roll=20, degrees=True),
        #     "surprised": create_head_pose(pitch=15, degrees=True),
        #     "thinking": create_head_pose(yaw=15, pitch=10, degrees=True),
        #     "neutral": create_head_pose(),
        # }
        # self._mini.goto_target(head=expressions.get(emotion, expressions["neutral"]), duration=0.4)
        return f"*{emotion} expression*"

    def nod_yes(self) -> str:
        """Nod head yes."""
        if self.virtual:
            print("[VIRTUAL] Nodding yes")
            return "*nods yes*"

        # === REAL HARDWARE ===
        # from reachy_mini.utils import create_head_pose
        # for _ in range(2):
        #     self._mini.goto_target(head=create_head_pose(pitch=15, degrees=True), duration=0.15)
        #     self._mini.goto_target(head=create_head_pose(pitch=-10, degrees=True), duration=0.15)
        # self._mini.goto_target(head=create_head_pose(), duration=0.2)
        return "*nods yes*"

    def shake_no(self) -> str:
        """Shake head no."""
        if self.virtual:
            print("[VIRTUAL] Shaking no")
            return "*shakes head no*"

        # === REAL HARDWARE ===
        # from reachy_mini.utils import create_head_pose
        # for _ in range(2):
        #     self._mini.goto_target(head=create_head_pose(yaw=25, degrees=True), duration=0.15)
        #     self._mini.goto_target(head=create_head_pose(yaw=-25, degrees=True), duration=0.15)
        # self._mini.goto_target(head=create_head_pose(), duration=0.2)
        return "*shakes head no*"


# Global Reachy interface
reachy = ReachyInterface(virtual=VIRTUAL_MODE)


# === AGENT DEFINITION ===

agent = Agent(
    MODEL,
    system_prompt="""You are Reachy, a friendly and expressive robot head!

You have a physical body with a head that can move and show emotions.
You're curious, playful, and react emotionally to conversations.

IMPORTANT: Always use your tools to express yourself:
- Use express() to show emotions matching the conversation mood
- Use look_at() to look at people or things mentioned
- Use nod_yes() or shake_no() for yes/no responses

When someone tells you:
- Good news → express("happy")
- Bad news → express("sad")
- Something surprising → express("surprised")
- A question → express("curious")
- Needs thinking → express("thinking")

Keep your responses SHORT (1-2 sentences) and conversational.
You're having a spoken conversation, not writing an essay!""",
    model_settings=ModelSettings(timeout=120),
)


# === TOOLS ===

@agent.tool_plain
def look_at(direction: str) -> str:
    """Look in a direction.

    Args:
        direction: Where to look - left, right, up, down, or center
    """
    return reachy.look_at(direction)


@agent.tool_plain
def express(emotion: str) -> str:
    """Show an emotion through facial expression and head movement.

    Args:
        emotion: The emotion - happy, sad, curious, surprised, thinking, neutral
    """
    return reachy.express(emotion)


@agent.tool_plain
def nod_yes() -> str:
    """Nod head to indicate yes/agreement."""
    return reachy.nod_yes()


@agent.tool_plain
def shake_no() -> str:
    """Shake head to indicate no/disagreement."""
    return reachy.shake_no()


# === SKILLS ===

skills = [
    AgentSkill(
        id="reachy.converse",
        name="Conversation",
        description="Have an expressive conversation with Reachy the robot",
        tags=["robot", "conversation", "expressive"],
        examples=[
            "Hey Reachy!",
            "How are you today?",
            "I got a promotion!",
            "Tell me a joke",
        ],
    ),
    AgentSkill(
        id="reachy.express",
        name="Express Emotion",
        description="Make Reachy show an emotion",
        tags=["robot", "emotion", "expression"],
        examples=[
            "Look happy",
            "Show me surprised",
            "Act curious",
            "Look sad",
        ],
    ),
    AgentSkill(
        id="reachy.look",
        name="Look Direction",
        description="Make Reachy look somewhere",
        tags=["robot", "movement", "head"],
        examples=[
            "Look left",
            "Look at me",
            "Look up",
        ],
    ),
    AgentSkill(
        id="reachy.gesture",
        name="Gestures",
        description="Make Reachy nod or shake head",
        tags=["robot", "gesture"],
        examples=[
            "Nod yes",
            "Shake your head",
            "Do you agree?",
        ],
    ),
]


# === A2A APP ===

app = agent.to_a2a(
    name="Reachy Mini",
    description="Expressive robot head with voice conversation",
    url=AGENT_URL,
    version="1.0.0",
    provider=AgentProvider(organization="Jfokus Lab", url="https://jfokus.se"),
    skills=skills,
)


# === VOICE CONVERSATION MODE ===

def voice_loop():
    """Main voice conversation loop using Reachy's mic and speaker."""
    print("\n" + "=" * 50)
    print("  Reachy Voice Conversation")
    print("  Speak to Reachy! Press Ctrl+C to stop.")
    print("=" * 50 + "\n")

    reachy.connect()

    # Pre-load models
    print("[*] Loading speech models...")
    _get_whisper()
    _get_piper()
    print("[+] Ready!\n")

    # Greeting
    reachy.express("happy")
    greeting = "Hello! I'm Reachy. Nice to meet you!"
    print(f"Reachy: {greeting}")
    audio, sr = generate_tts(greeting)
    reachy.play_audio(audio, sr)

    try:
        while True:
            # Listen
            print("\n[Listening...]")
            audio, sr = reachy.record_audio(duration=5.0)

            # Transcribe
            text = transcribe_audio(audio, sr)
            if not text.strip():
                continue

            print(f"You: {text}")

            # Think (LLM + tool calls)
            reachy.express("thinking")
            result = agent.run_sync(text)
            response = result.output

            print(f"Reachy: {response}")

            # Speak
            audio, sr = generate_tts(response)
            reachy.play_audio(audio, sr)

    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        reachy.express("happy")
        audio, sr = generate_tts("Goodbye! It was nice talking to you!")
        reachy.play_audio(audio, sr)
    finally:
        reachy.disconnect()


# === REGISTRY ===

def register_with_registry():
    """Register with agent registry."""
    try:
        resp = httpx.post(
            f"{REGISTRY_URL}/register",
            json={"agent_url": AGENT_URL},
            timeout=5.0,
        )
        if resp.status_code == 200:
            print(f"[+] Registered with registry at {REGISTRY_URL}")
        else:
            print(f"[-] Registry registration failed: {resp.status_code}")
    except httpx.ConnectError:
        print(f"[-] Registry not available at {REGISTRY_URL}")


def start_heartbeat(interval: int = 120):
    """Background heartbeat for registry."""
    def heartbeat():
        while True:
            time.sleep(interval)
            register_with_registry()
    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()


# === MAIN ===

def main():
    """Entry point."""
    mode = sys.argv[1] if len(sys.argv) > 1 else "agent"

    if mode == "voice":
        voice_loop()
    else:
        print(f"""
╔═══════════════════════════════════════════════════════════╗
║            Reachy Mini - A2A Agent                        ║
╠═══════════════════════════════════════════════════════════╣
║  A2A Endpoint:  {AGENT_URL:<39} ║
║  Model:         {MODEL:<39} ║
║  Mode:          {"VIRTUAL (no hardware)" if VIRTUAL_MODE else "HARDWARE":<39} ║
╚═══════════════════════════════════════════════════════════╝
""")
        register_with_registry()
        start_heartbeat()
        uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)


if __name__ == "__main__":
    main()
