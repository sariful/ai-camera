"""
Display Manager Module for AI Camera System

Handles frame processing, synchronization, and display of multiple camera feeds.
"""

import cv2
import time
import numpy as np
from config import CAMERA_SETTINGS, DISPLAY_SETTINGS, TEXT_SETTINGS, APP_CONSTANTS


class DisplayManager:
    """
    Manages the display of multiple camera feeds with synchronization and frame processing.
    """
    
    def __init__(self):
        """Initialize the display manager."""
        self.target_frame_time = 1.0 / DISPLAY_SETTINGS["target_fps"]
        
    def create_placeholder_frame(self, camera_id):
        """
        Create a placeholder frame for disconnected cameras.
        
        Args:
            camera_id (int): Camera identifier
            
        Returns:
            numpy.ndarray: Black frame with disconnection message
        """
        placeholder = np.zeros((CAMERA_SETTINGS["frame_height"], CAMERA_SETTINGS["frame_width"], 3), dtype=np.uint8)
        cv2.putText(placeholder, f"Camera {camera_id + 1} Disconnected", 
                   APP_CONSTANTS["placeholder_text_pos"], 
                   eval(TEXT_SETTINGS["font"]), 
                   TEXT_SETTINGS["font_scale_large"], 
                   TEXT_SETTINGS["color_red"], 
                   TEXT_SETTINGS["thickness"])
        return placeholder
    
    def collect_frames(self, camera_threads):
        """
        Collect latest frames from all camera threads.
        
        Args:
            camera_threads (list): List of CameraThread instances
            
        Returns:
            tuple: (frames, timestamps) lists
        """
        frames = []
        timestamps = []
        
        for cam_thread in camera_threads:
            frame, timestamp = cam_thread.get_latest_frame()
            if frame is not None:
                frames.append(frame)
                timestamps.append(timestamp)
            else:
                # Create placeholder for disconnected camera
                placeholder = self.create_placeholder_frame(cam_thread.camera_id)
                frames.append(placeholder)
                timestamps.append(0)
                
        return frames, timestamps
    
    def check_synchronization(self, timestamps):
        """
        Check frame synchronization across cameras.
        
        Args:
            timestamps (list): List of frame timestamps
            
        Returns:
            float: Maximum time difference between frames
        """
        if len(timestamps) > 1:
            valid_timestamps = [t for t in timestamps if t > 0]
            if len(valid_timestamps) > 1:
                max_time_diff = max(valid_timestamps) - min(valid_timestamps)
                if max_time_diff > DISPLAY_SETTINGS["sync_threshold"]:
                    print(f"⏱️ Frame time difference: {max_time_diff:.3f}s")
                return max_time_diff
        return 0.0
    
    def combine_frames(self, frames):
        """
        Combine multiple frames side by side.
        
        Args:
            frames (list): List of frame arrays
            
        Returns:
            numpy.ndarray: Combined frame
        """
        if not frames:
            return None
        return np.hstack(frames)
    
    def add_overlay_info(self, combined_frame):
        """
        Add informational overlay to the combined frame.
        
        Args:
            combined_frame (numpy.ndarray): Combined frame to add overlay to
        """
        cv2.putText(combined_frame, f"FPS Target: {DISPLAY_SETTINGS['target_fps']} | Sync Check", 
                   (10, 30), 
                   eval(TEXT_SETTINGS["font"]), 
                   TEXT_SETTINGS["font_scale"], 
                   TEXT_SETTINGS["color_green"], 
                   TEXT_SETTINGS["thickness"])
    
    def display_frame(self, combined_frame):
        """
        Display the combined frame.
        
        Args:
            combined_frame (numpy.ndarray): Frame to display
        """
        if combined_frame is not None:
            cv2.imshow(DISPLAY_SETTINGS["window_title"], combined_frame)
    
    def calculate_delay(self, start_time):
        """
        Calculate appropriate delay to maintain target FPS.
        
        Args:
            start_time (float): Frame processing start time
            
        Returns:
            int: Delay in milliseconds for cv2.waitKey
        """
        elapsed = time.time() - start_time
        delay = max(APP_CONSTANTS["min_delay"], int((self.target_frame_time - elapsed) * 1000))
        return delay
    
    def process_frame_cycle(self, camera_threads):
        """
        Process one complete frame cycle for all cameras.
        
        Args:
            camera_threads (list): List of CameraThread instances
            
        Returns:
            bool: True to continue, False to quit
        """
        start_time = time.time()
        
        # Collect frames from all cameras
        frames, timestamps = self.collect_frames(camera_threads)
        
        if frames:
            # Check synchronization
            self.check_synchronization(timestamps)
            
            # Combine frames
            combined = self.combine_frames(frames)
            
            # Add overlay information
            self.add_overlay_info(combined)
            
            # Display the combined frame
            self.display_frame(combined)
        
        # Maintain consistent timing
        delay = self.calculate_delay(start_time)
        
        # Check for quit key
        if cv2.waitKey(delay) & 0xFF == APP_CONSTANTS["quit_key"]:
            return False
        
        return True
    
    def cleanup(self):
        """Clean up display resources."""
        cv2.destroyAllWindows()