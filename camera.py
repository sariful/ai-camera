import cv2
import time
import numpy as np
import threading
from collections import deque

# 🔗 RTSP URLs for 3 channels (adjust username, password, IP, ports if needed)
URLS = [
    "rtsp://admin:pass12345@192.168.0.103:554/cam/realmonitor?channel=2&subtype=1",
    "rtsp://admin:pass12345@192.168.0.103:554/cam/realmonitor?channel=1&subtype=1",
    "rtsp://admin:pass12345@192.168.0.103:554/cam/realmonitor?channel=4&subtype=1"
]

class CameraThread:
    def __init__(self, url, camera_id):
        self.url = url
        self.camera_id = camera_id
        self.cap = None
        self.frame = None
        self.timestamp = 0
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    def open_stream(self):
        if self.cap:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # minimize buffer
        self.cap.set(cv2.CAP_PROP_FPS, 25)
        return self.cap.isOpened()

    def start(self):
        if self.open_stream():
            self.running = True
            self.thread = threading.Thread(target=self._capture_loop)
            self.thread.daemon = True
            self.thread.start()
            return True
        return False

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()

    def _capture_loop(self):
        while self.running:
            if not self.cap or not self.cap.isOpened():
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    print(f"🔄 Reconnecting Camera {self.camera_id + 1}... (attempt {self.reconnect_attempts + 1})")
                    if self.open_stream():
                        self.reconnect_attempts = 0
                    else:
                        self.reconnect_attempts += 1
                        time.sleep(1)
                        continue
                else:
                    print(f"❌ Camera {self.camera_id + 1} failed after {self.max_reconnect_attempts} attempts")
                    time.sleep(5)  # Wait longer before trying again
                    self.reconnect_attempts = 0
                    continue

            ret, frame = self.cap.read()
            if ret and frame is not None:
                # Resize frame immediately to reduce processing time
                frame = cv2.resize(frame, (640, 360))
                
                with self.lock:
                    self.frame = frame.copy()
                    self.timestamp = time.time()
                    self.reconnect_attempts = 0
            else:
                print(f"⚠️ Failed to read from Camera {self.camera_id + 1}")
                time.sleep(0.1)

    def get_latest_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None, self.timestamp

# Initialize camera threads
camera_threads = []
for i, url in enumerate(URLS):
    cam_thread = CameraThread(url, i)
    camera_threads.append(cam_thread)

# Start all camera threads
for cam_thread in camera_threads:
    if cam_thread.start():
        print(f"✅ Camera {cam_thread.camera_id + 1} started successfully")
    else:
        print(f"❌ Failed to start Camera {cam_thread.camera_id + 1}")

print("🎥 All cameras initialized. Press 'q' to quit.")

try:
    while True:
        start_time = time.time()
        frames = []
        timestamps = []
        
        # Get latest frames from all cameras simultaneously
        for cam_thread in camera_threads:
            frame, timestamp = cam_thread.get_latest_frame()
            if frame is not None:
                frames.append(frame)
                timestamps.append(timestamp)
            else:
                # Create black placeholder for disconnected camera
                placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
                cv2.putText(placeholder, f"Camera {cam_thread.camera_id + 1} Disconnected", 
                           (150, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                frames.append(placeholder)
                timestamps.append(0)

        # Only proceed if we have frames
        if frames:
            # Check timestamp synchronization (optional diagnostic)
            if len(timestamps) > 1:
                max_time_diff = max(timestamps) - min([t for t in timestamps if t > 0])
                if max_time_diff > 0.1:  # More than 100ms difference
                    print(f"⏱️ Frame time difference: {max_time_diff:.3f}s")

            # Arrange frames side by side (3 cameras horizontally)
            combined = np.hstack(frames)
            
            # Add timestamp info on the combined image
            cv2.putText(combined, f"FPS Target: 25 | Sync Check", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow("3 Cameras - Synchronized", combined)

        # Maintain consistent timing
        elapsed = time.time() - start_time
        target_frame_time = 1.0 / 25.0  # 25 FPS target
        delay = max(1, int((target_frame_time - elapsed) * 1000))
        
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\n🛑 Stopping cameras...")

finally:
    # Clean shutdown
    for cam_thread in camera_threads:
        cam_thread.stop()
    cv2.destroyAllWindows()
    print("✅ All cameras stopped successfully")
