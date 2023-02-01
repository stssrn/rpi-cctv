import cv2
import socketio

from decouple import config
from ultralytics import YOLO

from camera import Camera

HOST = config("MIDDLEWARE_HOST")
PORT = config("MIDDLEWARE_PORT")

# initialize YOLOv8
model = YOLO("yolov8n.pt")

sio = socketio.Client()
sio.connect(f"http://{HOST}:{PORT}/", namespaces=["/device"])
with Camera() as cam:
    for frame in cam.frames():
        # send frame to middleware
        _, jpeg = cv2.imencode(".jpg", frame)
        sio.emit("frame", jpeg.tobytes(), namespace="/device")

        # only run object detection once per second
        if cam.frame_count % cam.framerate != 0:
            continue

        for prediction in model.predict(source=frame, stream=True):
            boxes = prediction.boxes
            for cls in boxes.cls:
                person_class = 0
                if cls == person_class:
                    sio.emit("detected", namespace="/device")
