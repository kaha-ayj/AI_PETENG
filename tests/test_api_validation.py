from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


client = TestClient(app)


class FakePredictionService:
    def predict(self, image_bytes):
        return {
            "ai_status": "selesai",
            "photo_status": "layak_dinilai",
            "lighting_class": "redup",
            "confidence": 0.91,
            "model_version": "test-model",
            "message": "Foto berhasil dianalisis.",
        }




def image_bytes(format_name: str = "JPEG") -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (32, 32), color="navy").save(buffer, format=format_name)
    return buffer.getvalue()


def test_validate_accepts_valid_jpeg(monkeypatch):
    monkeypatch.setattr("app.api.routes.prediction_service", FakePredictionService())
    response = client.post(
        "/api/v1/ai/validate",
        files={"image": ("road.jpg", image_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == response.json()["request_id"]
    assert response.json()["ai_status"] == "selesai"
    assert response.json()["lighting_class"] == "redup"
    assert response.json()["confidence"] == 0.91


def test_validate_rejects_unsupported_media_type():
    response = client.post(
        "/api/v1/ai/validate",
        files={"image": ("notes.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_validate_rejects_invalid_image_content():
    response = client.post(
        "/api/v1/ai/validate",
        files={"image": ("fake.jpg", b"not an image", "image/jpeg")},
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "INVALID_IMAGE"
