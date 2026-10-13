from dataclasses import dataclass


@dataclass(frozen=True)
class AIConfig:
    model_version: str = "mock-yolo-cnn-v1"
    yolo_threshold: float = 0.5
    cnn_threshold: float = 0.7
    min_objects_for_valid: int = 1


CONFIG = AIConfig()
