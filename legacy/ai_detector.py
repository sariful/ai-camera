"""
AI Detection Module for Human Detection using YOLOv8

Handles YOLOv8 model loading, inference, and human detection processing.
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Optional
import time
import torch


class HumanDetector:
    """
    Human detection using YOLOv8 model.
    Specifically detects humans (class 0 in COCO dataset) in camera frames.
    """
    
    def __init__(self, model_name: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize the human detector.
        
        Args:
            model_name (str): YOLOv8 model variant ('yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', etc.)
            confidence_threshold (float): Minimum confidence score for detections
        """
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.model_loaded = False
        
        # Force CPU usage (no GPU required)
        self.device = 'cpu'
        torch.set_default_tensor_type('torch.FloatTensor')  # Ensure CPU tensors
        
        self.detection_stats = {
            'total_detections': 0,
            'total_frames_processed': 0,
            'avg_inference_time': 0.0,
            'last_detection_count': 0
        }
        
        # COCO class names - person is class 0
        self.human_class_id = 0
        
        # Initialize model
        self._load_model()
    
    def _load_model(self) -> bool:
        """
        Load the YOLOv8 model.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            print(f"🤖 Loading YOLOv8 model: {self.model_name} (CPU mode)")
            self.model = YOLO(self.model_name)
            
            # Explicitly move model to CPU
            self.model.to(self.device)
            
            # Run a dummy inference to warm up the model
            dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
            _ = self.model(dummy_frame, verbose=False, device=self.device)
            
            self.model_loaded = True
            print(f"✅ YOLOv8 model loaded successfully on CPU!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load YOLOv8 model: {e}")
            self.model_loaded = False
            return False
    
    def detect_humans(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect humans in a single frame.
        
        Args:
            frame (np.ndarray): Input frame (BGR format)
            
        Returns:
            List[Tuple[int, int, int, int, float]]: List of (x1, y1, x2, y2, confidence) for each human detection
        """
        if not self.model_loaded:
            return []
        
        start_time = time.time()
        
        try:
            # Run inference with CPU device explicitly specified
            results = self.model(frame, verbose=False, device=self.device)
            
            human_detections = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get class ID and confidence
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        
                        # Only keep human detections above confidence threshold
                        if class_id == self.human_class_id and confidence >= self.confidence_threshold:
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                            human_detections.append((x1, y1, x2, y2, confidence))
            
            # Update statistics
            inference_time = time.time() - start_time
            self._update_stats(len(human_detections), inference_time)
            
            return human_detections
            
        except Exception as e:
            print(f"⚠️ Error during human detection: {e}")
            return []
    
    def draw_detections(self, frame: np.ndarray, detections: List[Tuple[int, int, int, int, float]], 
                       camera_id: int = 0) -> np.ndarray:
        """
        Draw bounding boxes and labels on the frame for detected humans.
        
        Args:
            frame (np.ndarray): Input frame
            detections (List[Tuple]): List of detection tuples (x1, y1, x2, y2, confidence)
            camera_id (int): Camera identifier for labeling
            
        Returns:
            np.ndarray: Frame with drawn detections
        """
        annotated_frame = frame.copy()
        
        for i, (x1, y1, x2, y2, confidence) in enumerate(detections):
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Prepare label
            label = f"Human {i+1}: {confidence:.2f}"
            
            # Get text size for background
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            
            # Draw label background
            cv2.rectangle(annotated_frame, (x1, y1 - text_height - 10), 
                         (x1 + text_width, y1), (0, 255, 0), -1)
            
            # Draw label text
            cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Draw detection summary
        summary_text = f"Cam {camera_id + 1}: {len(detections)} humans detected"
        cv2.putText(annotated_frame, summary_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return annotated_frame
    
    def _update_stats(self, detection_count: int, inference_time: float):
        """
        Update detection statistics.
        
        Args:
            detection_count (int): Number of humans detected in this frame
            inference_time (float): Time taken for inference in seconds
        """
        self.detection_stats['total_detections'] += detection_count
        self.detection_stats['total_frames_processed'] += 1
        self.detection_stats['last_detection_count'] = detection_count
        
        # Update rolling average of inference time
        total_frames = self.detection_stats['total_frames_processed']
        current_avg = self.detection_stats['avg_inference_time']
        self.detection_stats['avg_inference_time'] = (
            (current_avg * (total_frames - 1) + inference_time) / total_frames
        )
    
    def get_stats(self) -> dict:
        """
        Get detection statistics.
        
        Returns:
            dict: Dictionary containing detection statistics
        """
        return self.detection_stats.copy()
    
    def is_model_loaded(self) -> bool:
        """
        Check if the model is loaded and ready for inference.
        
        Returns:
            bool: True if model is loaded, False otherwise
        """
        return self.model_loaded
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.
        
        Returns:
            dict: Model information
        """
        return {
            'model_name': self.model_name,
            'confidence_threshold': self.confidence_threshold,
            'model_loaded': self.model_loaded,
            'target_class': 'person (COCO class 0)'
        }