"""
Configuration module for AI Camera System

Contains all configuration parameters, RTSP URLs, and constants used throughout the application.
"""

# 🔗 RTSP URLs for 3 channels (adjust username, password, IP, ports if needed)
RTSP_URLS = [
    "rtsp://admin:pass12345@192.168.0.103:554/cam/realmonitor?channel=2&subtype=1",
    "rtsp://admin:pass12345@192.168.0.103:554/cam/realmonitor?channel=1&subtype=1",
    "rtsp://admin:pass12345@192.168.0.103:554/cam/realmonitor?channel=4&subtype=1"
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