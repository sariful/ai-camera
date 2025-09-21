import os
from dotenv import load_dotenv
import cv2, time, threading, requests
from ultralytics import YOLO
import pygame

# Load env variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Split comma-separated cameras into a list and strip whitespace
CAMERAS = [cam.strip() for cam in os.getenv("CAMERAS", "").split(",") if cam.strip()]

model = YOLO("yolov8n.pt")

def processDetections(frame, cam_num, timestamp):
    print(f"Processing detections for Camera {cam_num} at {timestamp}")
    # Play alert sound

    try:
        filename = f"dumps/{cam_num}_{int(timestamp)}.jpg"
        cv2.imwrite(filename, frame)
    except Exception as e:
        print(f"⚠️ Error saving image: {e}")
    
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("assets/beep-329314.mp3")
        pygame.mixer.music.play()
        print(f"🔊 Playing alert sound for detection on Camera {cam_num}")
    except Exception as e:
        print(f"⚠️ Error playing sound: {e}")

def process_camera(cam_url, cam_num):
    cap = cv2.VideoCapture(cam_url)
    last_sent = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue
        results = model.predict(frame, classes=[0], conf=0.6, verbose=False)
        if len(results[0].boxes) > 0:
            now = time.time()
            if now - last_sent > 5:
                processDetections(frame, cam_num, now)
                last_sent = now
    cap.release()

threads = []
for i, url in enumerate(CAMERAS, start=1):
    t = threading.Thread(target=process_camera, args=(url, i), daemon=True)
    t.start()
    threads.append(t)

print("Monitoring started for all cameras.")
while True:
    time.sleep(60)
