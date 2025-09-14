"""
Test script to verify the new 2-row camera layout logic
"""

import numpy as np
import cv2
import sys
import os

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from display_manager import DisplayManager

def create_test_frame(camera_id, width=400, height=280):
    """Create a test frame with camera ID displayed"""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add different colors for each camera to distinguish them
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (255, 0, 255)]  # Red, Green, Blue, Yellow, Magenta
    color = colors[camera_id % len(colors)]
    frame[:] = color
    
    # Add camera number text
    cv2.putText(frame, f"Camera {camera_id + 1}", 
                (width//2 - 60, height//2), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1.0, 
                (255, 255, 255), 
                2)
    
    return frame

def test_layout():
    """Test the new 2-row layout with different numbers of cameras"""
    display_manager = DisplayManager()
    
    # Test with 1 camera
    print("Testing with 1 camera...")
    frames_1 = [create_test_frame(0)]
    combined_1 = display_manager.combine_frames(frames_1)
    cv2.imwrite("test_1_camera.png", combined_1)
    
    # Test with 2 cameras
    print("Testing with 2 cameras...")
    frames_2 = [create_test_frame(0), create_test_frame(1)]
    combined_2 = display_manager.combine_frames(frames_2)
    cv2.imwrite("test_2_cameras.png", combined_2)
    
    # Test with 3 cameras (our main use case)
    print("Testing with 3 cameras...")
    frames_3 = [create_test_frame(0), create_test_frame(1), create_test_frame(2)]
    combined_3 = display_manager.combine_frames(frames_3)
    cv2.imwrite("test_3_cameras.png", combined_3)
    
    # Test with 4 cameras
    print("Testing with 4 cameras...")
    frames_4 = [create_test_frame(0), create_test_frame(1), create_test_frame(2), create_test_frame(3)]
    combined_4 = display_manager.combine_frames(frames_4)
    cv2.imwrite("test_4_cameras.png", combined_4)
    
    print("Test completed! Check the generated PNG files:")
    print("- test_1_camera.png: Single camera")
    print("- test_2_cameras.png: Two cameras side by side")
    print("- test_3_cameras.png: 2 cameras on top, 1 centered below")
    print("- test_4_cameras.png: 2 cameras on top, 2 cameras below")
    
    print(f"\n3-camera layout dimensions: {combined_3.shape}")

if __name__ == "__main__":
    try:
        test_layout()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure OpenCV and NumPy are installed:")
        print("pip install opencv-python numpy")
    except Exception as e:
        print(f"Error during testing: {e}")