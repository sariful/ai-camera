"""
Configuration module for AI Camera System

Contains all configuration parameters, RTSP URLs, and constants used throughout the application.
"""

import os
import subprocess
from typing import Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_screen_resolution() -> Tuple[int, int]:
    """
    Get the current screen resolution using multiple fallback methods.
    
    Returns:
        Tuple[int, int]: Screen width and height in pixels
    """
    try:
        # Method 1: Try tkinter (most reliable if available)
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        return screen_width, screen_height
    except ImportError:
        pass
    
    try:
        # Method 2: Try xrandr command (Linux)
        result = subprocess.run(['xrandr'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if ' connected primary ' in line or ' connected ' in line:
                    # Look for resolution pattern like "1920x1080"
                    import re
                    match = re.search(r'(\d+)x(\d+)', line)
                    if match:
                        return int(match.group(1)), int(match.group(2))
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass
    
    try:
        # Method 3: Try xdpyinfo command (Linux)
        result = subprocess.run(['xdpyinfo'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            import re
            width_match = re.search(r'dimensions:\s*(\d+)x(\d+)', result.stdout)
            if width_match:
                return int(width_match.group(1)), int(width_match.group(2))
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Method 4: Check common environment variables
    try:
        if 'DISPLAY' in os.environ:
            # We're likely on a Linux system with X11
            # Common resolutions for modern displays
            return 1920, 1080
    except:
        pass
    
    print("⚠️ Could not detect screen resolution using any method")
    # Return common fallback resolution
    return 1920, 1080


def calculate_optimal_frame_size(screen_width: int, screen_height: int, 
                                num_cameras: int = 3, aspect_ratio: float = 16/9) -> Tuple[int, int]:
    """
    Calculate optimal frame size based on screen resolution and camera layout.
    
    Args:
        screen_width (int): Screen width in pixels
        screen_height (int): Screen height in pixels  
        num_cameras (int): Number of cameras to display (default: 3)
        aspect_ratio (float): Desired aspect ratio for camera frames (default: 16/9)
        
    Returns:
        Tuple[int, int]: Optimal frame width and height
    """
    # Reserve space for window decorations and taskbar (about 10% of screen)
    usable_width = int(screen_width * 0.9)
    usable_height = int(screen_height * 0.85)
    
    # Calculate layout based on number of cameras
    if num_cameras <= 2:
        # Single row layout
        cols, rows = num_cameras, 1
    else:
        # Multi-row layout (2 cameras on top, rest below)
        cols, rows = 2, 2
    
    # Calculate maximum frame size that fits in the layout
    max_frame_width = usable_width // cols
    max_frame_height = usable_height // rows
    
    # Maintain aspect ratio
    # Try width-constrained first
    width_constrained_width = max_frame_width
    width_constrained_height = int(max_frame_width / aspect_ratio)
    
    # Try height-constrained
    height_constrained_height = max_frame_height
    height_constrained_width = int(max_frame_height * aspect_ratio)
    
    # Choose the option that fits both constraints
    if width_constrained_height <= max_frame_height:
        frame_width = width_constrained_width
        frame_height = width_constrained_height
    else:
        frame_width = height_constrained_width
        frame_height = height_constrained_height
    
    # Ensure minimum reasonable size
    min_width, min_height = 320, 240
    frame_width = max(frame_width, min_width)
    frame_height = max(frame_height, min_height)
    
    # Ensure maximum reasonable size (prevent oversized windows)
    max_width, max_height = 800, 600
    frame_width = min(frame_width, max_width)
    frame_height = min(frame_height, max_height)
    
    return frame_width, frame_height


# Get dynamic frame dimensions based on screen size
try:
    screen_width, screen_height = get_screen_resolution()
    DYNAMIC_FRAME_WIDTH, DYNAMIC_FRAME_HEIGHT = calculate_optimal_frame_size(screen_width, screen_height)
    print(f"📺 Screen resolution detected: {screen_width}x{screen_height}")
    print(f"📏 Calculated optimal frame size: {DYNAMIC_FRAME_WIDTH}x{DYNAMIC_FRAME_HEIGHT}")
except Exception as e:
    # Fallback to static values if screen detection fails
    DYNAMIC_FRAME_WIDTH, DYNAMIC_FRAME_HEIGHT = 400, 280
    print(f"⚠️ Could not detect screen size ({e}). Using fallback frame dimensions: {DYNAMIC_FRAME_WIDTH}x{DYNAMIC_FRAME_HEIGHT}")

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
    "frame_width": DYNAMIC_FRAME_WIDTH,   # Dynamically calculated frame width based on screen size
    "frame_height": DYNAMIC_FRAME_HEIGHT, # Dynamically calculated frame height based on screen size
    "max_reconnect_attempts": 5, # Maximum reconnection attempts
    "reconnect_delay": 1,       # Delay between reconnection attempts (seconds)
    "extended_retry_delay": 5   # Extended delay after max attempts (seconds)
}

# Display settings
DISPLAY_SETTINGS = {
    "target_fps": 25,           # Target display FPS
    "sync_threshold": 2,      # Maximum acceptable time difference for sync (seconds)
    "window_title": "3 Cameras - 2x2 Grid Layout"
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
    "placeholder_text_pos": (DYNAMIC_FRAME_WIDTH//2 - 100, DYNAMIC_FRAME_HEIGHT//2)  # Centered position for disconnected camera text
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