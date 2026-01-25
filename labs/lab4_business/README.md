# Lab 4: Business Readiness Coach

> **Physical Agent Lab Series**
> AI is moving from the digital world into the physical world. This lab demonstrates an agentic loop - the AI coach evaluates multiple aspects, gives feedback, and offers retries for improvement.

Multi-turn agentic coach that checks your readiness for business meetings.

## What it does

The coach takes ONE photo and evaluates 4 aspects:
1. **Clothing** - Professional attire?
2. **Grooming** - Hair tidy?
3. **Background** - Appropriate for video calls?
4. **Pose** - Confident expression, no funny faces?

Flow:
- Captures your photo (3-second countdown)
- Analyzes all 4 aspects with Vision LLM (separate calls for focused evaluation)
- Shows all scores (1-10) and spoken feedback
- If any score < 7, offers to retry with a new photo
- Gives final summary and verdict

## Prerequisites

```bash
ollama pull gemma3:4b
```

## Setup

```bash
pixi install
```

## Usage

```bash
pixi run demo
```

## Example Session

```
🎯 Business Readiness Coach
I'll check your: clothing, grooming, background, and pose.

[Takes photo with 3-second countdown]

Analyzing your photo...
  Analyzing clothing...
  Analyzing grooming...
  Analyzing background...
  Analyzing pose...

----------------------------------------
📋 CLOTHING: 8/10
   Nice shirt, professional look. Collar is slightly askew.

📋 GROOMING: 6/10
   Hair looks a bit messy on one side.

📋 BACKGROUND: 7/10
   Clean background, no distractions.

📋 POSE: 9/10
   Great posture and confident expression.

========================================
📊 SUMMARY
  Clothing     8/10
  Grooming     6/10
  Background   7/10
  Pose         9/10

  AVERAGE      7.5/10

🎯 Pretty good! A few small tweaks and you'll be perfect.

🔄 Try again? (y/n): y

[Makes adjustments, takes new photo...]

ROUND 2
========================================
...
```

## Components

- **Vision:** OpenCV webcam
- **VLM:** Ollama gemma3:4b (multimodal)
- **TTS:** Piper neural voice
- **Loop:** Multi-turn with retry option
