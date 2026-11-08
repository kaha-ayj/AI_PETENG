from pathlib import Path

import torch

from scripts.evaluate_classifier import evaluate


def test_evaluate_writes_report_for_test_split(tmp_path, monkeypatch):
    dataset_root = Path("dataset")
    checkpoint = Path("model_weights/resnet18-peteng-v1.pt")
    output_root = tmp_path / "reports"

    result = evaluate(dataset_root, checkpoint, output_root, batch_size=4)

    assert result["dataset_split"] == "test"
    assert result["sample_count"] == 8
    assert 0 <= result["accuracy"] <= 1
    assert 0 <= result["macro_f1"] <= 1
    assert (output_root / "classification_report.json").exists()
    assert (output_root / "confusion_matrix.png").exists()
    assert (output_root / "predictions.csv").exists()
