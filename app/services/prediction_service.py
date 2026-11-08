from __future__ import annotations

from io import BytesIO
from pathlib import Path

import torch
from PIL import Image, ImageOps
from torchvision import transforms

from app.core.config import CONFIDENCE_THRESHOLD, MODEL_PATH, MODEL_VERSION
from app.models.cnn_classifier import CLASS_NAMES, IMAGE_SIZE, ModelConfig, create_model


class ModelUnavailableError(Exception):
    pass


class InferenceError(Exception):
    pass


class PredictionService:
    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        model_version: str = MODEL_VERSION,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
    ):
        self.model_path = model_path
        self.model_version = model_version
        self.confidence_threshold = confidence_threshold
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self._transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

    @property
    def loaded(self) -> bool:
        return self.model is not None

    def load(self) -> None:
        if not self.model_path.exists():
            raise ModelUnavailableError(f"Checkpoint tidak ditemukan: {self.model_path}")
        try:
            model = create_model(ModelConfig(pretrained=False))
            state = torch.load(self.model_path, map_location=self.device, weights_only=True)
            model.load_state_dict(state)
            model.to(self.device)
            model.eval()
            self.model = model
        except (OSError, RuntimeError, ValueError) as error:
            raise ModelUnavailableError("Checkpoint model tidak dapat dimuat.") from error

    def predict(self, image_bytes: bytes) -> dict[str, object]:
        if not self.loaded:
            self.load()
        try:
            with Image.open(BytesIO(image_bytes)) as source:
                image = ImageOps.exif_transpose(source).convert("RGB")
                tensor = self._transform(image).unsqueeze(0).to(self.device)
            with torch.inference_mode():
                probabilities = torch.softmax(self.model(tensor), dim=1)[0]
            confidence, index = probabilities.max(dim=0)
            label = CLASS_NAMES[int(index)]
            score = float(confidence)
        except (OSError, RuntimeError, ValueError) as error:
            raise InferenceError("Inferensi gambar gagal.") from error

        if score < self.confidence_threshold:
            return {
                "ai_status": "perlu_tinjauan_manual",
                "photo_status": "perlu_tinjauan",
                "lighting_class": None,
                "confidence": score,
                "model_version": self.model_version,
                "message": "Confidence model belum cukup untuk memberikan hasil otomatis.",
            }
        if label == "bukan_jalan":
            return {
                "ai_status": "selesai",
                "photo_status": "tidak_layak",
                "lighting_class": None,
                "confidence": score,
                "model_version": self.model_version,
                "message": "Foto tidak menunjukkan jalan yang relevan untuk dianalisis.",
            }
        return {
            "ai_status": "selesai",
            "photo_status": "layak_dinilai",
            "lighting_class": label,
            "confidence": score,
            "model_version": self.model_version,
            "message": "Foto berhasil dianalisis.",
        }
