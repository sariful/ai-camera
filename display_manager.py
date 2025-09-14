"""
Display Manager Module for AI Camera System

Handles frame processing, synchronization, display of multiple camera feeds, and AI-based human detection.
"""

import cv2
import time
import numpy as np
import pygame
import threading
import os
from config import CAMERA_SETTINGS, DISPLAY_SETTINGS, TEXT_SETTINGS, APP_CONSTANTS, AI_DETECTION_SETTINGS
from ai_detector import HumanDetector


class DisplayManager:
    """
    Manages the display of multiple camera feeds with synchronization, frame processing, and AI-based human detection.
    """
    
    def __init__(self):
        """Initialize the display manager with AI detection capabilities."""
        self.target_frame_time = 1.0 / DISPLAY_SETTINGS["target_fps"]
        
        # Initialize AI detection
        self.human_detector = None
        if AI_DETECTION_SETTINGS["enabled"]:
            try:
                self.human_detector = HumanDetector(
                    model_name=AI_DETECTION_SETTINGS["model_name"],
                    confidence_threshold=AI_DETECTION_SETTINGS["confidence_threshold"]
                )
                print("🤖 AI Human Detection initialized successfully!")
            except Exception as e:
                print(f"⚠️ Failed to initialize AI detection: {e}")
                print("📷 Continuing without AI detection...")
                self.human_detector = None
        
        # Initialize sound system
        self.sound_initialized = False
        self.last_sound_time = 0
        self._init_sound_system()
        
    def _init_sound_system(self):
        """Initialize pygame mixer for sound playback."""
        if not AI_DETECTION_SETTINGS["sound_alert"]:
            return
            
        try:
            pygame.mixer.init()
            self.sound_initialized = True
            print("🔊 Sound system initialized successfully!")
            
            # Verify sound file exists
            sound_file = AI_DETECTION_SETTINGS["alert_sound_file"]
            if not os.path.exists(sound_file):
                print(f"⚠️ Sound file not found: {sound_file}")
                self.sound_initialized = False
            else:
                print(f"✅ Sound file found: {sound_file}")
                
        except Exception as e:
            print(f"⚠️ Failed to initialize sound system: {e}")
            self.sound_initialized = False
            
    def _play_alert_sound(self):
        """Play the alert sound in a separate thread to avoid blocking."""
        if not self.sound_initialized or not AI_DETECTION_SETTINGS["sound_alert"]:
            return
            
        current_time = time.time()
        cooldown = AI_DETECTION_SETTINGS["alert_cooldown"]
        
        # Check cooldown period
        if current_time - self.last_sound_time < cooldown:
            return
            
        def play_sound():
            try:
                sound_file = AI_DETECTION_SETTINGS["alert_sound_file"]
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                print(f"🔊 Playing alert sound for human detection on camera 3")
            except Exception as e:
                print(f"⚠️ Error playing sound: {e}")
                
        # Play sound in a separate thread to avoid blocking the main loop
        sound_thread = threading.Thread(target=play_sound, daemon=True)
        sound_thread.start()
        
        self.last_sound_time = current_time
        
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
    
    def apply_ai_detection(self, frames, camera_threads):
        """
        Apply AI-based human detection to frames.
        
        Args:
            frames (list): List of camera frames
            camera_threads (list): List of CameraThread instances
            
        Returns:
            list: Frames with AI detection annotations
        """
        if not self.human_detector or not AI_DETECTION_SETTINGS["enabled"]:
            return frames
        
        processed_frames = []
        
        for i, frame in enumerate(frames):
            camera_id = camera_threads[i].camera_id if i < len(camera_threads) else i
            
            # Check if detection should be applied to this camera
            if (AI_DETECTION_SETTINGS["detection_on_all_cameras"] or 
                camera_id in AI_DETECTION_SETTINGS["target_cameras"]):
                
                # Skip detection if frame is a placeholder (all zeros in top-left corner)
                if np.sum(frame[0:50, 0:50]) == 0:  # Likely a placeholder frame
                    processed_frames.append(frame)
                    continue
                
                try:
                    # Detect humans in the frame
                    detections = self.human_detector.detect_humans(frame)
                    
                    # Limit detections if specified
                    max_detections = AI_DETECTION_SETTINGS["max_detections_per_frame"]
                    if len(detections) > max_detections:
                        detections = detections[:max_detections]
                    
                    # Check if this is camera 3 (index 2) and play sound if humans detected
                    if (detections and 
                        AI_DETECTION_SETTINGS["sound_alert"] and 
                        camera_id == AI_DETECTION_SETTINGS["sound_alert_camera"]):
                        self._play_alert_sound()
                    
                    # Draw detections if enabled
                    if AI_DETECTION_SETTINGS["draw_bounding_boxes"] and detections:
                        frame = self.human_detector.draw_detections(frame, detections, camera_id)
                    
                except Exception as e:
                    print(f"⚠️ AI detection error for camera {camera_id}: {e}")
            
            processed_frames.append(frame)
        
        return processed_frames
    
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
        Combine multiple frames in a 2-row layout:
        - First row: 2 cameras
        - Second row: remaining cameras
        
        Args:
            frames (list): List of frame arrays
            
        Returns:
            numpy.ndarray: Combined frame
        """
        if not frames:
            return None
        
        num_cameras = len(frames)
        if num_cameras == 0:
            return None
        
        # Ensure all frames have the same dimensions
        frame_height, frame_width = frames[0].shape[:2]
        
        if num_cameras == 1:
            return frames[0]
        elif num_cameras == 2:
            # Just place both cameras side by side in one row
            return np.hstack(frames)
        else:
            # 2-row layout: first row gets 2 cameras, second row gets the rest
            cameras_first_row = 2
            cameras_second_row = num_cameras - cameras_first_row
            
            # Create first row with first 2 cameras
            first_row = np.hstack(frames[:cameras_first_row])
            
            # Create second row with remaining cameras
            if cameras_second_row == 1:
                # If only one camera in second row, center it by adding padding
                second_row = frames[cameras_first_row]
                # Add padding to match width of first row
                padding_width = first_row.shape[1] - second_row.shape[1]
                if padding_width > 0:
                    left_padding = padding_width // 2
                    right_padding = padding_width - left_padding
                    left_pad = np.zeros((frame_height, left_padding, 3), dtype=np.uint8)
                    right_pad = np.zeros((frame_height, right_padding, 3), dtype=np.uint8)
                    second_row = np.hstack([left_pad, second_row, right_pad])
            else:
                # Multiple cameras in second row
                second_row = np.hstack(frames[cameras_first_row:])
                # Add padding if second row is narrower than first row
                width_diff = first_row.shape[1] - second_row.shape[1]
                if width_diff > 0:
                    padding = np.zeros((frame_height, width_diff, 3), dtype=np.uint8)
                    second_row = np.hstack([second_row, padding])
            
            # Combine both rows vertically
            combined = np.vstack([first_row, second_row])
            return combined
    
    def add_overlay_info(self, combined_frame):
        """
        Add informational overlay to the combined frame.
        
        Args:
            combined_frame (numpy.ndarray): Combined frame to add overlay to
        """
    
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
        Process one complete frame cycle for all cameras with AI detection.
        
        Args:
            camera_threads (list): List of CameraThread instances
            
        Returns:
            bool: True to continue, False to quit
        """
        start_time = time.time()
        
        # Collect frames from all cameras
        frames, timestamps = self.collect_frames(camera_threads)
        
        if frames:
            # Apply AI detection to frames
            frames = self.apply_ai_detection(frames, camera_threads)
            
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
        """Clean up display resources and AI detector."""
        cv2.destroyAllWindows()
        
        # Cleanup sound system
        if self.sound_initialized:
            try:
                pygame.mixer.quit()
                print("🔊 Sound system cleaned up successfully!")
            except Exception as e:
                print(f"⚠️ Error cleaning up sound system: {e}")
        
        # Print AI detection statistics if available
        if self.human_detector and AI_DETECTION_SETTINGS["enabled"]:
            stats = self.human_detector.get_stats()
            print(f"\n🤖 AI Detection Statistics:")
            print(f"   Total frames processed: {stats['total_frames_processed']}")
            print(f"   Total humans detected: {stats['total_detections']}")
            print(f"   Average inference time: {stats['avg_inference_time']:.3f}s")
            if stats['total_frames_processed'] > 0:
                print(f"   Detection rate: {stats['total_detections']/stats['total_frames_processed']:.2f} humans/frame")