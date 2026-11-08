from __future__ import annotations

import os
from pathlib import Path


ALLOWED_IMAGE_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
MIN_IMAGE_WIDTH = int(os.getenv("MIN_IMAGE_WIDTH", "10"))
MIN_IMAGE_HEIGHT = int(os.getenv("MIN_IMAGE_HEIGHT", "10"))
PROJECT_ROOT = Path(__file__).resolve().parents[2]
_configured_model_path = Path(os.getenv("MODEL_PATH", "model_weights/resnet18-peteng-v1.pt"))
MODEL_PATH = (
    _configured_model_path
    if _configured_model_path.is_absolute()
    else PROJECT_ROOT / _configured_model_path
)
MODEL_VERSION = os.getenv("MODEL_VERSION", "resnet18-peteng-v1")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))
