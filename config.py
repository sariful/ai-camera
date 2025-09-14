"""
Configuration module for AI Camera System

Contains all configuration parameters, RTSP URLs, and constants used throughout the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get RTSP credentials from environment variables
RTSP_USERNAME = os.getenv('RTSP_USERNAME', 'admin')
RTSP_PASSWORD = os.getenv('RTSP_PASSWORD')
RTSP_HOST = os.getenv('RTSP_HOST', '192.168.0.103')
RTSP_PORT = os.getenv('RTSP_PORT', '554')

# Validate that password is provided
if not RTSP_PASSWORD:
    raise ValueError(
        "RTSP_PASSWORD environment variable is required. "
        "Please set it in your .env file or environment."
    )

# 🔗 RTSP URLs for 3 channels (credentials loaded from environment variables)
RTSP_URLS = [
    f"rtsp://{RTSP_USERNAME}:{RTSP_PASSWORD}@{RTSP_HOST}:{RTSP_PORT}/cam/realmonitor?channel=2&subtype=1",
    f"rtsp://{RTSP_USERNAME}:{RTSP_PASSWORD}@{RTSP_HOST}:{RTSP_PORT}/cam/realmonitor?channel=1&subtype=1",
    f"rtsp://{RTSP_USERNAME}:{RTSP_PASSWORD}@{RTSP_HOST}:{RTSP_PORT}/cam/realmonitor?channel=4&subtype=1"
]

# Camera settings
CAMERA_SETTINGS = {
    "buffer_size": 1,           # Minimize buffer for low latency
    "fps": 25,                  # Target FPS
    "frame_width": 400,         # Resized frame width
    "frame_height": 280,        # Resized frame height
    "max_reconnect_attempts": 5, # Maximum reconnection attempts
    "reconnect_delay": 1,       # Delay between reconnection attempts (seconds)
    "extended_retry_delay": 5   # Extended delay after max attempts (seconds)
}

# Display settings
DISPLAY_SETTINGS = {
    "target_fps": 25,           # Target display FPS
    "sync_threshold": 2,      # Maximum acceptable time difference for sync (seconds)
    "window_title": "3 Cameras - Synchronized"
}

# Text overlay settings
TEXT_SETTINGS = {
    "font": "cv2.FONT_HERSHEY_SIMPLEX",
    "font_scale": 0.7,
    "font_scale_large": 1.0,
    "color_green": (0, 255, 0),
    "color_red": (0, 0, 255),
    "thickness": 2
}

# Application constants
APP_CONSTANTS = {
    "quit_key": ord('q'),       # Key to quit application
    "min_delay": 1,             # Minimum delay for cv2.waitKey (ms)
    "placeholder_text_pos": (150, 180)  # Position for disconnected camera text
}

# AI Detection settings
AI_DETECTION_SETTINGS = {
    "enabled": True,            # Enable/disable AI detection
    "model_name": "yolov8m.pt", # YOLOv8 model variant (n=nano, s=small, m=medium, l=large, x=extra-large)
    "confidence_threshold": 0.5, # Minimum confidence score for detections (0.0-1.0)
    "detection_on_all_cameras": True,  # Apply detection to all cameras or specific ones
    "target_cameras": [0, 1, 2], # Camera indices to apply detection (0-based)
    "draw_bounding_boxes": True, # Draw bounding boxes around detected humans
    "show_confidence": True,    # Show confidence scores in labels
    "detection_color": (0, 255, 0), # Color for bounding boxes (BGR format)
    "text_color": (0, 0, 0),    # Color for detection labels (BGR format)
    "box_thickness": 2,         # Thickness of bounding boxes
    "max_detections_per_frame": 10, # Maximum number of detections to process per frame
    "enable_stats_overlay": True,    # Show detection statistics on frames
    "stats_position": (10, 30)      # Position for stats text overlay
}