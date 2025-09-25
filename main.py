import os
import cv2, time, threading, json
from ultralytics import YOLO
from utils.camera_config import CameraManager
from utils.person_id import person_id
from utils.send_message import send_telegram_message
from utils.sound_alert import sound_alert
from utils.connect_camera import connect_camera
from utils.save_image import save_image

script_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize camera manager with configuration from config.json
config_path = os.path.join(script_dir, 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

camera_manager = CameraManager(config["cameras"])
MODEL = os.path.join(script_dir, f"{config['model']}.pt")

model = YOLO(MODEL)
model.fuse()  # Optimize model for inference

def processDetections(frame, camera_config, timestamp):
    print(f"Processing detections for Camera {camera_config.name} at {timestamp}")

    if camera_config.features.person_identification:
        person_id(frame=frame, camera_config=camera_config, timestamp=timestamp)

    if camera_config.features.save_images:
        image_path = save_image(frame=frame, camera_config=camera_config, timestamp=timestamp)

    if camera_config.features.send_message:
        send_telegram_message(image_path=image_path, text=f"🚨 Detection on Camera: {camera_config.name} at {timestamp}")
    
    if camera_config.features.sound_alert:
        sound_alert()
        print(f"🔊 Playing alert sound for detection on Camera: {camera_config.name}")

def process_camera(camera_config):
    cap = None
    last_sent = 0
    connection_lost = False
    
    while True:
        if cap is None:
            cap = connect_camera(camera_config)
            if cap is None:
                time.sleep(2)  # Wait before retry
                continue
        
        ret, frame = cap.read()
        if not ret:
            if not connection_lost:
                print(f"⚠️ Lost connection to camera {camera_config.name}")
                connection_lost = True
            cap.release()
            cap = None
            time.sleep(1)
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
            time.sleep(0.1)  # Brief pause before next frame
                    
# Start a thread for each camera
threads = []
for camera in camera_manager.get_cameras():
    t = threading.Thread(
        target=process_camera, 
        args=(camera,), 
        daemon=True,
        name=camera.name
    )
    t.start()
    threads.append(t)
    print(f"Started monitoring camera: {camera.name} (ID: {camera.id})")

print(f"Monitoring started for {len(threads)} cameras.")
while True:
    time.sleep(30)  # Reduced sleep time for better responsiveness
