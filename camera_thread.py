"""
Camera Thread Module for AI Camera System

Handles individual camera streams with threading, reconnection logic, and frame management.
"""

import cv2
import time
import threading
from config import CAMERA_SETTINGS


class CameraThread:
    """
    Manages a single camera stream in a separate thread with automatic reconnection capabilities.
    """
    
    def __init__(self, url, camera_id):
        """
        Initialize camera thread.
        
        Args:
            url (str): RTSP URL for the camera
            camera_id (int): Unique identifier for this camera
        """
        self.url = url
        self.camera_id = camera_id
        self.cap = None
        self.frame = None
        self.timestamp = 0
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = CAMERA_SETTINGS["max_reconnect_attempts"]

    def open_stream(self):
        """
        Open or reopen the camera stream.
        
        Returns:
            bool: True if stream opened successfully, False otherwise
        """
        if self.cap:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_SETTINGS["buffer_size"])
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_SETTINGS["fps"])
        return self.cap.isOpened()

    def start(self):
        """
        Start the camera thread.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self.open_stream():
            self.running = True
            self.thread = threading.Thread(target=self._capture_loop)
            self.thread.daemon = True
            self.thread.start()
            return True
        return False

    def stop(self):
        """Stop the camera thread and clean up resources."""
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()

    def _capture_loop(self):
        """
        Main capture loop running in a separate thread.
        Handles frame capture, resizing, and reconnection logic.
        """
        while self.running:
            if not self.cap or not self.cap.isOpened():
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    print(f"🔄 Reconnecting Camera {self.camera_id + 1}... (attempt {self.reconnect_attempts + 1})")
                    if self.open_stream():
                        self.reconnect_attempts = 0
                    else:
                        self.reconnect_attempts += 1
                        time.sleep(CAMERA_SETTINGS["reconnect_delay"])
                        continue
                else:
                    print(f"❌ Camera {self.camera_id + 1} failed after {self.max_reconnect_attempts} attempts")
                    time.sleep(CAMERA_SETTINGS["extended_retry_delay"])
                    self.reconnect_attempts = 0
                    continue

            ret, frame = self.cap.read()
            if ret and frame is not None:
                # Resize frame immediately to reduce processing time
                frame = cv2.resize(frame, (CAMERA_SETTINGS["frame_width"], CAMERA_SETTINGS["frame_height"]))
                
                with self.lock:
                    self.frame = frame.copy()
                    self.timestamp = time.time()
                    self.reconnect_attempts = 0
            else:
                print(f"⚠️ Failed to read from Camera {self.camera_id + 1}")
                time.sleep(0.1)

    def get_latest_frame(self):
        """
        Get the latest frame and timestamp.
        
        Returns:
            tuple: (frame, timestamp) where frame is numpy array or None
        """
        with self.lock:
            return self.frame.copy() if self.frame is not None else None, self.timestamp

    def is_connected(self):
        """
        Check if camera is currently connected.
        
        Returns:
            bool: True if connected and capturing frames, False otherwise
        """
        return self.cap is not None and self.cap.isOpened() and self.frame is not None

    def get_camera_info(self):
        """
        Get camera information for debugging.
        
        Returns:
            dict: Camera information including ID, URL, and connection status
        """
        return {
            "id": self.camera_id,
            "url": self.url,
            "connected": self.is_connected(),
            "reconnect_attempts": self.reconnect_attempts,
            "last_frame_time": self.timestamp
        }