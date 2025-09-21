import os
import cv2, time, threading, json
from ultralytics import YOLO
import pygame
from utils.camera_config import CameraManager


# Initialize camera manager with configuration from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

print(config["cameras"])

camera_manager = CameraManager(config["cameras"])
MODEL = f"{config["model"]}.pt"

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

def connect_camera(camera_config, max_attempts=None):
    """Attempts to connect to the camera with exponential backoff."""
    base_delay = 1  # Start with 1 second delay
    max_delay = 30  # Maximum delay between attempts
    attempt = 0
    
    while max_attempts is None or attempt < max_attempts:
        attempt += 1
        try:
            cap = cv2.VideoCapture(camera_config.url)
            if cap.isOpened():
                print(f"✅ Successfully connected to camera {camera_config.name} (attempt {attempt})")
                return cap
        except Exception as e:
            print(f"⚠️ Error connecting to camera {camera_config.name}: {str(e)}")
        
        # Calculate next delay with exponential backoff
        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
        print(f"⏳ Retrying connection to camera {camera_config.name} in {delay} seconds...")
        time.sleep(delay)
    
    return None

def process_camera(camera_config):
    cap = None
    last_sent = 0
    connection_lost = False
    
    while True:
        if cap is None:
            cap = connect_camera(camera_config)
            if cap is None:
                continue
        
        ret, frame = cap.read()
        if not ret:
            if not connection_lost:
                print(f"⚠️ Lost connection to camera {camera_config.name}")
                connection_lost = True
            cap.release()
            cap = None
            continue
        
        # Reset connection_lost flag when we successfully read a frame
        if connection_lost:
            print(f"✅ Restored connection to camera {camera_config.name}")
            connection_lost = False

        try:
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
        except Exception as e:
            print(f"⚠️ Error processing frame from camera {camera_config.name}: {str(e)}")
            time.sleep(1)  # Brief pause before next frame
                    
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
