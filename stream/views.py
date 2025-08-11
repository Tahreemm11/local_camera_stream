import cv2
from django.http import StreamingHttpResponse, HttpResponse
from ultralytics import YOLO
import numpy as np
import os

# Path to your YOLO model
MODEL_PATH = r"C:\Users\asdf\local_camera_stream\yolov8s-face-lindevs.pt"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"YOLO model not found at {MODEL_PATH}")

# Load YOLO model into RAM
model = YOLO(MODEL_PATH)

def generate_frames():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Run YOLO inference
        results = model.predict(frame, imgsz=640, conf=0.35, verbose=False)

        for r in results:
            if len(r.boxes) == 0:
                continue

            xyxy = r.boxes.xyxy.cpu().numpy()
            confs = r.boxes.conf.cpu().numpy()
            clss = r.boxes.cls.cpu().numpy()

            for (x1, y1, x2, y2), conf, cls in zip(xyxy, confs, clss):
                x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
                label = f"{r.names[int(cls)]} {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, max(y1-10, 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

def camera_feed(request):
    return StreamingHttpResponse(
        generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

def home(request):
    return HttpResponse("""
        <h1>Local Camera Stream</h1>
        <p>Click below to view live camera feed with YOLO face detection:</p>
        <a href="/stream/camera/">📷 Open Camera Feed</a>
    """)
