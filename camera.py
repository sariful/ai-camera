import cv2
import time
import numpy as np
import threading

# 🔗 RTSP URLs for 3 channels
URLS = [
    "rtsp://admin:pass12345@192.168.0.103:554/cam/realmonitor?channel=2&subtype=1",
    "rtsp://admin:pass12345@192.168.0.103:554/cam/realmonitor?channel=1&subtype=1",
    "rtsp://admin:pass12345@192.168.0.103:554/cam/realmonitor?channel=4&subtype=1"
]

# Shared frame storage
frames = [None] * len(URLS)
locks = [threading.Lock() for _ in URLS]

def capture_camera(url, index):
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (400, 280))
            with locks[index]:
                frames[index] = frame

# Start camera threads
for i, url in enumerate(URLS):
    thread = threading.Thread(target=capture_camera, args=(url, i))
    thread.daemon = True
    thread.start()

# Main display loop
time.sleep(1)  # Give cameras time to connect

while True:
    display_frames = []
    
    # Get current frames from all cameras
    for i in range(len(URLS)):
        with locks[i]:
            if frames[i] is not None:
                display_frames.append(frames[i].copy())
            else:
                # Black placeholder if camera not ready
                display_frames.append(np.zeros((280, 400, 3), dtype=np.uint8))
    
    # Combine and show
    if display_frames:
        combined = np.hstack(display_frames)
        cv2.imshow("3 Cameras - Synced", combined)
    
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
