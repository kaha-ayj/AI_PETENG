from io import BytesIO

import torch
from PIL import Image

from app.services.prediction_service import PredictionService


def image_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (32, 32), color="navy").save(buffer, format="JPEG")
    return buffer.getvalue()


def test_prediction_service_reports_manual_review_when_threshold_is_impossible(tmp_path):
    service = PredictionService(
        model_path=tmp_path / "missing.pt",
        confidence_threshold=1.1,
    )

    service.model = torch.nn.Sequential(
        torch.nn.Flatten(),
        torch.nn.Linear(3 * 224 * 224, 4),
    )
    service.model.eval()
    service._transform = service._transform

    result = service.predict(image_bytes())

    assert result["ai_status"] == "perlu_tinjauan_manual"
    assert result["photo_status"] == "perlu_tinjauan"
    assert result["lighting_class"] is None
