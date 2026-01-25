# Lab 2: Vision

> **Physical Agent Lab Series**
> AI is moving from the digital world into the physical world. In this lab series, we explore how AI can control real devices - robot arms, smart homes, and more. Vision gives physical agents the ability to perceive and understand their environment.

Real-time object detection and segmentation using YOLO 11 - fully local.

## Components

- **Detection:** YOLO 11n (bounding boxes, 80 classes)
- **Segmentation:** YOLO 11n-seg (pixel masks)

## Setup

```bash
pixi install
```

## Usage

```bash
pixi run demo        # Live webcam with bounding boxes
pixi run segment     # Live webcam with segmentation masks
pixi run detect      # Single frame detection
pixi run list-classes  # Show all 80 detectable classes
```

Press `q` to quit webcam views.

## Models

Models are downloaded automatically on first run:
- `yolo11n.pt` (~5MB) - detection
- `yolo11n-seg.pt` (~6MB) - segmentation

## API

```python
from main import detect_objects, segment_objects
import cv2

# Capture frame
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# Detect objects (returns list of dicts)
detections = detect_objects(frame, confidence=0.5)
# [{"class": "person", "confidence": 0.95, "box": [x1,y1,x2,y2]}, ...]

# Segment objects (returns detections + mask overlay)
detections, mask_overlay = segment_objects(frame, confidence=0.5)
```

## Classes

YOLO can detect 80 classes including: person, car, dog, cat, bottle, chair, phone, laptop, etc.
