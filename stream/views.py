# stream/views.py
import cv2
import numpy as np
import os
from django.http import StreamingHttpResponse, HttpResponse
from ultralytics import YOLO
from .utils import update_expression_for_face

# === YOLO Model Path ===
MODEL_PATH = r"C:\Users\asdf\local_camera_stream\yolov8s-face-lindevs.pt"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"YOLO model not found at {MODEL_PATH}")

# === Load YOLO Model Once ===
model = YOLO(MODEL_PATH)


def get_camera():
    """Open the default webcam using DirectShow backend (avoids MSMF warnings on Windows)."""
    return cv2.VideoCapture(0, cv2.CAP_DSHOW)


def generate_frames():
    """Capture frames, detect faces, run expression recognition, and yield MJPEG stream."""
    cap = get_camera()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_idx = 0
    process_every_n_frames = 4  # Process every Nth frame for speed
    last_detections = []        # Store recent detections to avoid blinking
    max_missed_frames = 6
    missed_since_last = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        display_boxes = []

        # Run YOLO on every Nth frame
        if frame_idx % process_every_n_frames == 0:
            results = model.predict(frame, imgsz=640, conf=0.30, verbose=False)
            found_any = False
            new_detections = []

            for r in results:
                if len(r.boxes) == 0:
                    continue

                xyxy = r.boxes.xyxy.cpu().numpy()
                for box in xyxy:
                    x1, y1, x2, y2 = map(int, box)

                    # Add a margin around the detected face
                    margin = 10
                    fx1 = max(0, x1 - margin)
                    fy1 = max(0, y1 - margin)
                    fx2 = min(frame.shape[1], x2 + margin)
                    fy2 = min(frame.shape[0], y2 + margin)

                    face_crop = frame[fy1:fy2, fx1:fx2].copy()
                    if face_crop.size == 0:
                        continue

                    face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)

                    try:
                        person, expr = update_expression_for_face(face_rgb)
                        label = f"{expr} #{person.face_id[:6]}"
                    except Exception as e:
                        print("update_expression_for_face error:", e)
                        label = "error"

                    new_detections.append((x1, y1, x2, y2, label))
                    found_any = True

            if found_any:
                last_detections = new_detections
                missed_since_last = 0
            else:
                missed_since_last += 1

        else:
            missed_since_last += 1

        # Show old detections if new ones are missing but still recent
        if last_detections and missed_since_last <= max_missed_frames:
            display_boxes = last_detections
        else:
            display_boxes = []

        # Clear detections if missed too many frames
        if missed_since_last > max_missed_frames:
            last_detections = []

        # Draw bounding boxes & labels
        for (x1, y1, x2, y2, label) in display_boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, max(y1 - 10, 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Encode frame as JPEG for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')

        frame_idx += 1

    cap.release()


def camera_feed(request):
    """Return a live MJPEG camera feed."""
    return StreamingHttpResponse(
        generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


def home(request):
    """Simple homepage with link to camera feed."""
    return HttpResponse("""
        <h1>Local Camera Stream</h1>
        <p>Click below to view live camera feed with YOLO + DeepFace:</p>
        <a href="/stream/camera/">📷 Open Camera Feed</a>
    """)
