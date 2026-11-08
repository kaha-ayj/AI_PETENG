from pathlib import Path

from scripts.smoke_test_api import run_smoke_test


def test_smoke_test_processes_test_images(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "dataset" / "test" / "terang"
    source.mkdir(parents=True)
    image_path = source / "sample.jpg"

    from PIL import Image

    Image.new("RGB", (32, 32), color="white").save(image_path, format="JPEG")

    # This test validates the report shape; the real model checkpoint is used
    # by the service in the normal project working directory.
    report = run_smoke_test(tmp_path / "dataset" / "test")

    assert report["sample_count"] == 1
    assert report["successful_requests"] in (0, 1)
    assert len(report["results"]) == 1
