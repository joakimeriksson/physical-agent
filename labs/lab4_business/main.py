#!/usr/bin/env python3
"""Lab 4: Business Readiness Coach

Multi-turn agentic loop that checks:
1. Clothing
2. Grooming (hair)
3. Background
4. Pose & expression

Prerequisites:
    ollama pull gemma3:4b

Usage:
    pixi run demo
"""

import base64
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import cv2
import numpy as np
import sounddevice as sd

# --- Config ---

MODEL = "gemma3:4b"
CHECKS = [
    ("clothing", "Evaluate their clothing and attire for a business meeting. Is it professional, casual, or too casual? Any issues like wrinkles, stains, or inappropriate items?"),
    ("grooming", "Evaluate their grooming and hair. Is it tidy and presentable? Any obvious issues?"),
    ("background", "Evaluate the background behind them. Is it appropriate for a video call? Any distracting or unprofessional items visible?"),
    ("pose", "Evaluate their pose and facial expression. Are they sitting up straight? Do they look confident and approachable? Any funny faces or awkward poses?"),
]

# Shared models directory
MODEL_DIR = Path(__file__).parent.parent.parent / "models"


# --- Camera ---

def capture_photo(message: str = "Get ready!") -> np.ndarray | None:
    """Capture a photo with live preview and countdown."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return None

    start_time = time.time()
    countdown = 3

    while countdown > 0:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        cv2.putText(display, str(countdown), (frame.shape[1]//2 - 50, frame.shape[0]//2 + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 10)
        cv2.putText(display, message, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Business Coach", display)
        cv2.waitKey(1)

        elapsed = time.time() - start_time
        countdown = 3 - int(elapsed)

    ret, frame = cap.read()
    cap.release()

    if ret:
        display = frame.copy()
        cv2.putText(display, "CAPTURED! Press any key...", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Business Coach", display)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return frame

    return None


def image_to_base64(image: np.ndarray) -> str:
    """Convert OpenCV image to base64."""
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')


# --- VLM ---

def analyze_aspect(image: np.ndarray, aspect: str, prompt: str) -> tuple[int, str]:
    """Analyze one aspect of the image. Returns (score, feedback)."""
    image_b64 = image_to_base64(image)

    full_prompt = f"""{prompt}

Give a score from 1-10 and brief feedback (2-3 sentences max).
Format your response EXACTLY like this:
SCORE: [number]
FEEDBACK: [your feedback]

Remember: This will be spoken aloud, so no markdown or special characters."""

    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "images": [image_b64],
        "stream": False,
    }

    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            text = result.get("response", "")

            # Parse score and feedback
            score = 5  # default
            feedback = text

            score_match = re.search(r'SCORE:\s*(\d+)', text)
            if score_match:
                score = int(score_match.group(1))

            feedback_match = re.search(r'FEEDBACK:\s*(.+)', text, re.DOTALL)
            if feedback_match:
                feedback = feedback_match.group(1).strip()

            return score, feedback
    except Exception as e:
        return 5, f"Could not analyze: {e}"


# --- TTS ---

_piper_voice = None


def download_piper_voice():
    """Download Piper voice if not present."""
    voice_dir = MODEL_DIR / "piper"
    voice_dir.mkdir(parents=True, exist_ok=True)

    onnx_path = voice_dir / "en_US-lessac-medium.onnx"
    json_path = voice_dir / "en_US-lessac-medium.onnx.json"

    if not onnx_path.exists():
        print("Downloading Piper voice...")
        base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium"
        urllib.request.urlretrieve(f"{base_url}/en_US-lessac-medium.onnx", onnx_path)
        urllib.request.urlretrieve(f"{base_url}/en_US-lessac-medium.onnx.json", json_path)

    return onnx_path


def _get_piper():
    """Load Piper voice (cached)."""
    global _piper_voice
    if _piper_voice is None:
        from piper import PiperVoice
        model_path = download_piper_voice()
        print("Loading TTS...")
        _piper_voice = PiperVoice.load(str(model_path))
    return _piper_voice


def clean_for_speech(text: str) -> str:
    """Remove markdown and special chars for TTS."""
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'`+', '', text)
    text = re.sub(r'_+', ' ', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def speak(text: str):
    """Speak text using Piper TTS."""
    text = clean_for_speech(text)
    voice = _get_piper()

    audio_arrays = []
    for chunk in voice.synthesize(text):
        audio_arrays.append(chunk.audio_float_array)

    audio = np.concatenate(audio_arrays) if audio_arrays else np.array([])
    sd.play(audio, samplerate=voice.config.sample_rate)
    sd.wait()


# --- Agentic Loop ---

def analyze_all_aspects(image: np.ndarray) -> dict:
    """Analyze all aspects of a single image. Returns {aspect: (score, feedback)}."""
    results = {}
    for aspect, prompt in CHECKS:
        print(f"  Analyzing {aspect}...")
        score, feedback = analyze_aspect(image, aspect, prompt)
        results[aspect] = (score, feedback)
    return results


def show_results(results: dict):
    """Display and speak all results."""
    print("\n" + "-" * 40)
    for aspect, (score, feedback) in results.items():
        print(f"📋 {aspect.upper()}: {score}/10")
        print(f"   {feedback}\n")

    # Speak summary
    for aspect, (score, feedback) in results.items():
        speak(f"For {aspect}, I give you {score} out of 10. {feedback}")


def calculate_summary(results: dict) -> tuple[float, str]:
    """Calculate average and verdict."""
    total = sum(score for score, _ in results.values())
    average = total / len(results) if results else 0

    if average >= 8:
        verdict = "Excellent! You're totally ready for that meeting. Go get them!"
    elif average >= 6:
        verdict = "Pretty good! A few small tweaks and you'll be perfect."
    elif average >= 4:
        verdict = "Some room for improvement. Consider the feedback I gave you."
    else:
        verdict = "Hmm, might want to do a bit more preparation before that meeting."

    return average, verdict


def run_coach():
    """Run the multi-turn business readiness coach."""
    print("\n🎯 Business Readiness Coach")
    print("=" * 40)
    print("I'll check your: clothing, grooming, background, and pose.")
    print("Let's make sure you're ready for that meeting!\n")

    speak("Hello! I'm your business readiness coach. Let's check if you're ready for your meeting.")

    while True:
        # Capture one photo
        speak("Get ready! I'll take your photo and evaluate you on all aspects.")
        image = capture_photo("Strike your best business pose!")
        if image is None:
            print("Could not capture photo. Exiting.")
            return

        # Analyze all 4 aspects on the same photo
        print("\nAnalyzing your photo...")
        results = analyze_all_aspects(image)

        # Show all results
        show_results(results)

        # Calculate and show summary
        average, verdict = calculate_summary(results)

        print("=" * 40)
        print("📊 SUMMARY")
        print("=" * 40)
        for aspect, (score, _) in results.items():
            print(f"  {aspect.capitalize():12} {score}/10")
        print(f"\n  {'AVERAGE':12} {average:.1f}/10")
        print(f"\n🎯 {verdict}")

        speak(f"Your average score is {average:.1f} out of 10. {verdict}")

        # Check if any score is low
        low_scores = [a for a, (s, _) in results.items() if s < 7]

        if low_scores:
            speak(f"I noticed some areas could be improved: {', '.join(low_scores)}. Would you like to try again?")
            print(f"\n🔄 Try again? (y/n): ", end="")
            try:
                response = input().strip().lower()
                if response == 'y':
                    speak("Okay, make your adjustments and let's try again!")
                    print("\n" + "=" * 40)
                    print("ROUND 2")
                    print("=" * 40)
                    continue
            except EOFError:
                pass

        # Done
        speak("Good luck with your meeting!")
        print("\nDone!")
        break


def main():
    run_coach()


if __name__ == "__main__":
    main()
