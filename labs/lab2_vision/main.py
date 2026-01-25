#!/usr/bin/env python3
"""Lab 2: Vision with YOLO object detection and segmentation

Uses YOLO 11 for real-time object detection and segmentation - fully local.

Usage:
    pixi run demo           # Live webcam detection (bounding boxes)
    pixi run detect         # Detect from single frame
    pixi run segment        # Live webcam segmentation (masks)
    pixi run list-classes   # Show detectable classes
"""

import sys

import cv2
import numpy as np

# --- YOLO Models ---

_models = {}


def _get_model(model_name: str = "yolo11n.pt"):
    """Load YOLO model (cached)."""
    if model_name not in _models:
        from ultralytics import YOLO
        print(f"Loading YOLO model '{model_name}'...")
        _models[model_name] = YOLO(model_name)
    return _models[model_name]


def detect_objects(image: np.ndarray, confidence: float = 0.5) -> list[dict]:
    """Detect objects in an image.

    Args:
        image: BGR image (from OpenCV)
        confidence: Minimum confidence threshold

    Returns:
        List of detections: [{"class": "person", "confidence": 0.95, "box": [x1,y1,x2,y2]}, ...]
    """
    model = _get_model()
    results = model(image, verbose=False)[0]

    detections = []
    for box in results.boxes:
        conf = float(box.conf[0])
        if conf >= confidence:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            xyxy = box.xyxy[0].tolist()
            detections.append({
                "class": cls_name,
                "confidence": round(conf, 2),
                "box": [int(x) for x in xyxy],
            })

    return detections


def draw_detections(image: np.ndarray, detections: list[dict]) -> np.ndarray:
    """Draw bounding boxes on image."""
    img = image.copy()

    for det in detections:
        x1, y1, x2, y2 = det["box"]
        label = f"{det['class']} {det['confidence']:.0%}"

        # Draw box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Draw label background
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (x1, y1 - 25), (x1 + w, y1), (0, 255, 0), -1)

        # Draw label text
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    return img


# --- Segmentation ---

def segment_objects(image: np.ndarray, confidence: float = 0.5) -> tuple[list[dict], np.ndarray]:
    """Segment objects in an image.

    Args:
        image: BGR image (from OpenCV)
        confidence: Minimum confidence threshold

    Returns:
        Tuple of (detections, mask_overlay)
    """
    model = _get_model("yolo11n-seg.pt")
    results = model(image, verbose=False)[0]

    detections = []
    mask_overlay = image.copy()

    if results.masks is not None:
        # Generate random colors for each detection
        colors = np.random.randint(0, 255, (len(results.boxes), 3), dtype=np.uint8)

        for i, (box, mask) in enumerate(zip(results.boxes, results.masks.data)):
            conf = float(box.conf[0])
            if conf >= confidence:
                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id]
                xyxy = box.xyxy[0].tolist()

                detections.append({
                    "class": cls_name,
                    "confidence": round(conf, 2),
                    "box": [int(x) for x in xyxy],
                })

                # Apply mask overlay
                mask_resized = cv2.resize(mask.cpu().numpy(), (image.shape[1], image.shape[0]))
                mask_bool = mask_resized > 0.5
                color = colors[i].tolist()
                mask_overlay[mask_bool] = (
                    mask_overlay[mask_bool] * 0.5 + np.array(color) * 0.5
                ).astype(np.uint8)

    return detections, mask_overlay


def draw_segment_labels(image: np.ndarray, detections: list[dict]) -> np.ndarray:
    """Draw labels on segmented image."""
    img = image.copy()

    for det in detections:
        x1, y1, x2, y2 = det["box"]
        label = f"{det['class']} {det['confidence']:.0%}"

        # Draw label background
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (x1, y1 - 25), (x1 + w, y1), (0, 0, 0), -1)
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    return img


def run_segment_webcam(confidence: float = 0.5):
    """Run live webcam segmentation."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    print("Starting webcam segmentation. Press 'q' to quit.")
    print(f"Confidence threshold: {confidence:.0%}")

    # Pre-load model
    _get_model("yolo11n-seg.pt")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Segment and draw
        detections, mask_overlay = segment_objects(frame, confidence)
        annotated = draw_segment_labels(mask_overlay, detections)

        # Show detection count
        cv2.putText(
            annotated,
            f"Objects: {len(detections)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        cv2.imshow("YOLO Segmentation", annotated)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def capture_frame() -> np.ndarray | None:
    """Capture a single frame from webcam."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return None

    ret, frame = cap.read()
    cap.release()

    return frame if ret else None


def run_webcam(confidence: float = 0.5):
    """Run live webcam detection."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    print("Starting webcam detection. Press 'q' to quit.")
    print(f"Confidence threshold: {confidence:.0%}")

    # Pre-load model
    _get_model()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect and draw
        detections = detect_objects(frame, confidence)
        annotated = draw_detections(frame, detections)

        # Show detection count
        cv2.putText(
            annotated,
            f"Objects: {len(detections)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        cv2.imshow("YOLO Detection", annotated)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def detect_single(confidence: float = 0.5):
    """Capture single frame and detect."""
    print("Capturing frame...")
    frame = capture_frame()

    if frame is None:
        return

    detections = detect_objects(frame, confidence)

    print(f"\nDetected {len(detections)} objects:")
    for det in detections:
        print(f"  - {det['class']}: {det['confidence']:.0%}")

    # Show result
    annotated = draw_detections(frame, detections)
    cv2.imshow("Detection", annotated)
    print("\nPress any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def list_classes():
    """List all detectable classes."""
    model = _get_model()
    print(f"\nYOLO can detect {len(model.names)} classes:\n")
    for i, name in model.names.items():
        print(f"  {i:3}: {name}")


# --- Main ---

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "webcam":
        conf = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
        run_webcam(conf)

    elif cmd == "detect":
        conf = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
        detect_single(conf)

    elif cmd == "segment" or cmd == "segment-webcam":
        conf = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
        run_segment_webcam(conf)

    elif cmd == "classes":
        list_classes()

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
