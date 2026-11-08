r"""Run a local API smoke test against the real CNN checkpoint.

Usage:
    .venv\Scripts\python.exe scripts/smoke_test_api.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def run_smoke_test(dataset_root: Path = Path("dataset/test")) -> dict:
    client = TestClient(app)
    results = []
    for image_path in sorted(dataset_root.rglob("*")):
        if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        response = client.post(
            "/api/v1/ai/validate",
            files={
                "image": (
                    image_path.name,
                    image_path.read_bytes(),
                    "image/jpeg" if image_path.suffix.lower() in {".jpg", ".jpeg"} else "image/png",
                )
            },
        )
        payload = response.json()
        results.append({
            "path": image_path.as_posix(),
            "expected_class": image_path.parent.name,
            "status_code": response.status_code,
            "ai_status": payload.get("ai_status"),
            "photo_status": payload.get("photo_status"),
            "lighting_class": payload.get("lighting_class"),
            "confidence": payload.get("confidence"),
            "error_code": payload.get("detail", {}).get("error_code") if isinstance(payload.get("detail"), dict) else None,
        })

    readiness = client.get("/api/v1/ai/ready")
    report = {
        "readiness": readiness.json(),
        "sample_count": len(results),
        "successful_requests": sum(item["status_code"] == 200 for item in results),
        "results": results,
    }
    Path("reports").mkdir(exist_ok=True)
    Path("reports/api_smoke_test.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    report = run_smoke_test()
    print(json.dumps({
        "readiness": report["readiness"],
        "sample_count": report["sample_count"],
        "successful_requests": report["successful_requests"],
        "report": "reports/api_smoke_test.json",
    }, indent=2))


if __name__ == "__main__":
    main()
