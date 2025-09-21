import cv2
import time

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