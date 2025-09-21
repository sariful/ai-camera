import os
from dotenv import load_dotenv
import cv2, time, threading, requests
from ultralytics import YOLO
import pygame
from camera_config import CameraManager

# Load env variables
load_dotenv()

# Initialize camera manager with configuration from .env
camera_manager = CameraManager(os.getenv("CAMERAS_CONFIG", "{}"))
MODEL = os.getenv("model", "yolov8n.pt")

model = YOLO(MODEL)

def processDetections(frame, camera_config, timestamp):
    print(f"Processing detections for Camera {camera_config.name} at {timestamp}")

    if camera_config.features.save_images:
        try:
            filename = f"dumps/{camera_config.id}_{int(timestamp)}.jpg"
            cv2.imwrite(filename, frame)
        except Exception as e:
            print(f"⚠️ Error saving image: {e}")
    
    if camera_config.features.sound_alert:
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("assets/beep-329314.mp3")
            pygame.mixer.music.play()
            print(f"🔊 Playing alert sound for detection on Camera {camera_config.name}")
        except Exception as e:
            print(f"⚠️ Error playing sound: {e}")

def process_camera(camera_config):
    cap = cv2.VideoCapture(camera_config.url)
    last_sent = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"⚠️ Failed to read frame from camera {camera_config.name}")
            time.sleep(1)
            continue

        if camera_config.features.human_detection:
            results = model.predict(
                frame, 
                classes=[0], 
                conf=camera_config.features.confidence_threshold,
                verbose=False
            )
            
            if len(results[0].boxes) > 0:
                now = time.time()
                if now - last_sent > 5:
                    processDetections(frame, camera_config, now)
                    last_sent = now
                    
    cap.release()

# Start a thread for each camera
threads = []
for camera in camera_manager.get_cameras():
    t = threading.Thread(
        target=process_camera, 
        args=(camera,), 
        daemon=True,
        name=f"Camera-{camera.name}"
    )
    t.start()
    threads.append(t)
    print(f"Started monitoring camera: {camera.name} (ID: {camera.id})")

print(f"Monitoring started for {len(threads)} cameras.")
while True:
    time.sleep(60)
