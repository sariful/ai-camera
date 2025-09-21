import json
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class CameraFeatures:
    human_detection: bool = True
    person_identification: bool = False
    sound_alert: bool = True
    confidence_threshold: float = 0.6
    save_images: bool = False
    send_message: bool = False

@dataclass
class CameraConfig:
    id: int
    name: str
    url: str
    features: CameraFeatures

class CameraManager:
    def __init__(self, cameras_config: list):
        self.cameras: List[CameraConfig] = []
        self._parse_config(cameras_config)

    def _parse_config(self, cameras_config: list):
        try:
            for camera in cameras_config:
                features = CameraFeatures(**camera['features'])
                camera_config = CameraConfig(
                    id=camera['id'],
                    name=camera['name'],
                    url=camera['url'],
                    features=features
                )
                self.cameras.append(camera_config)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid camera configuration JSON: {e}")
        except KeyError as e:
            raise ValueError(f"Missing required field in camera configuration: {e}")

    def get_camera(self, camera_id: int) -> CameraConfig:
        for camera in self.cameras:
            if camera.id == camera_id:
                return camera
        raise ValueError(f"Camera with ID {camera_id} not found")

    def get_cameras(self) -> List[CameraConfig]:
        return self.cameras