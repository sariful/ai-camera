import os
import cv2

script_dir = os.path.dirname(os.path.abspath(__file__))

def save_image(frame, camera_config, timestamp):
    try:
        dumps_dir = os.path.join(script_dir, "dumps")
        os.makedirs(dumps_dir, exist_ok=True)  # Ensure dumps directory exists
        filename = os.path.join(dumps_dir, f"{camera_config.name}_{timestamp}.jpg")
        cv2.imwrite(filename, frame)

        return filename
    except Exception as e:
        print(f"⚠️ Error saving image: {e}")