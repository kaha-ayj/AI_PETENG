from io import BytesIO

import torch
from PIL import Image

from app.services.prediction_service import PredictionService


def image_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (32, 32), color="navy").save(buffer, format="JPEG")
    return buffer.getvalue()


def test_prediction_service_returns_not_suitable_when_non_road_class_wins(tmp_path):
    service = PredictionService(model_path=tmp_path / "missing.pt")
    service.model = torch.nn.Sequential(
        torch.nn.Flatten(),
        torch.nn.Linear(3 * 224 * 224, 4),
    )
    service.model.eval()
    service.model[-1].weight.data.zero_()
    service.model[-1].bias.data[:] = torch.tensor([10.0, 0.0, 0.0, 0.0])

    result = service.predict(image_bytes())

    assert result == {
        "ai_status": "selesai",
        "photo_status": "tidak_layak",
        "lighting_class": None,
        "confidence": result["confidence"],
        "model_version": service.model_version,
        "message": "Foto tidak menampilkan kondisi jalan. Harap unggah ulang foto yang sesuai.",
    }
    assert result["confidence"] > 0.99


def test_prediction_service_returns_lighting_class_for_valid_photo(tmp_path):
    service = PredictionService(model_path=tmp_path / "missing.pt")
    service.model = torch.nn.Sequential(
        torch.nn.Flatten(),
        torch.nn.Linear(3 * 224 * 224, 4),
    )
    service.model.eval()
    service.model[-1].weight.data.zero_()
    service.model[-1].bias.data[:] = torch.tensor([0.0, 0.0, 10.0, 0.0])

    result = service.predict(image_bytes())

    assert result["ai_status"] == "selesai"
    assert result["photo_status"] == "layak_dinilai"
    assert result["lighting_class"] == "redup"
