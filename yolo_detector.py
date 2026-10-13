from typing import List, Dict, Any
from .config import CONFIG


def detect_objects(foto_url: str, kategori: str) -> Dict[str, Any]:
    # Placeholder deterministic detection until real YOLO weights are available.
    objects = [
        {
            "label": "lampu_pju",
            "confidence": 0.91,
            "bbox": {"x1": 10.0, "y1": 20.0, "x2": 120.0, "y2": 240.0},
        }
    ]
    yolo_confidence = 0.91 if objects else 0.0
    return {"objects": objects, "yolo_confidence": yolo_confidence}
