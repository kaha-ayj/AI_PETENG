import os
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_model_path_is_stable_when_imported_from_parent_directory():
    script = """
import sys
sys.path.insert(0, r'D:\\peteng-project\\ai_peteng')
from app.core.config import MODEL_PATH
assert MODEL_PATH.is_absolute()
assert MODEL_PATH.exists(), MODEL_PATH
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT.parent,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_error_response_matches_contract_without_detail_wrapper():
    response = TestClient(app).post(
        "/api/v1/ai/validate",
        files={"image": ("fake.jpg", b"not an image", "image/jpeg")},
        headers={"X-Request-ID": "contract-error-1"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "request_id": "contract-error-1",
        "ai_status": "gagal",
        "error_code": "INVALID_IMAGE",
        "message": "Isi file bukan gambar yang valid.",
    }
    assert "detail" not in response.json()
