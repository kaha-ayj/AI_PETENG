r"""Evaluate the CNN checkpoint on the held-out test split.

Usage:
    .venv\Scripts\python.exe scripts/evaluate_classifier.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
)
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.cnn_classifier import CLASS_NAMES, IMAGE_SIZE, ModelConfig, create_model


NORMALIZE = transforms.Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225],
)


def evaluation_transform():
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        NORMALIZE,
    ])


def evaluate(
    dataset_root: Path = Path("dataset"),
    checkpoint: Path = Path("model_weights/resnet18-peteng-v1.pt"),
    output_root: Path = Path("reports"),
    batch_size: int = 4,
) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    test_data = datasets.ImageFolder(dataset_root / "test", transform=evaluation_transform())
    expected_mapping = {name: index for index, name in enumerate(CLASS_NAMES)}
    if test_data.class_to_idx != expected_mapping:
        raise ValueError(f"Mapping kelas test tidak sesuai: {test_data.class_to_idx}")

    model = create_model(ModelConfig(pretrained=False))
    state = torch.load(checkpoint, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.to(device)
    model.eval()

    loader = DataLoader(test_data, batch_size=batch_size, shuffle=False)
    actual: list[int] = []
    predicted: list[int] = []
    confidences: list[float] = []
    predictions: list[dict[str, object]] = []

    with torch.inference_mode():
        for images, labels in loader:
            logits = model(images.to(device))
            probabilities = torch.softmax(logits, dim=1)
            confidence, indices = probabilities.max(dim=1)
            actual.extend(labels.tolist())
            predicted.extend(indices.cpu().tolist())
            confidences.extend(confidence.cpu().tolist())

    report = classification_report(
        actual,
        predicted,
        labels=list(range(len(CLASS_NAMES))),
        target_names=list(CLASS_NAMES),
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(actual, predicted, labels=list(range(len(CLASS_NAMES))))

    for (path, actual_index), predicted_index, confidence in zip(
        test_data.samples, predicted, confidences
    ):
        predictions.append({
            "path": str(Path(path).as_posix()),
            "actual": CLASS_NAMES[actual_index],
            "predicted": CLASS_NAMES[predicted_index],
            "confidence": round(confidence, 6),
            "correct": actual_index == predicted_index,
        })

    output_root.mkdir(parents=True, exist_ok=True)
    summary = {
        "model_version": "resnet18-peteng-v1",
        "checkpoint": checkpoint.as_posix(),
        "dataset_split": "test",
        "device": str(device),
        "classes": list(CLASS_NAMES),
        "sample_count": len(actual),
        "accuracy": report["accuracy"],
        "macro_f1": report["macro avg"]["f1-score"],
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
    }
    (output_root / "classification_report.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    with (output_root / "predictions.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["path", "actual", "predicted", "confidence", "correct"])
        writer.writeheader()
        writer.writerows(predictions)

    figure, axis = plt.subplots(figsize=(7, 7))
    ConfusionMatrixDisplay(matrix, display_labels=CLASS_NAMES).plot(
        ax=axis, cmap="Blues", values_format="d", colorbar=False
    )
    axis.set_title("AI PETENG — Confusion Matrix")
    figure.tight_layout()
    figure.savefig(output_root / "confusion_matrix.png", dpi=150)
    plt.close(figure)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=Path("dataset"))
    parser.add_argument("--checkpoint", type=Path, default=Path("model_weights/resnet18-peteng-v1.pt"))
    parser.add_argument("--output-root", type=Path, default=Path("reports"))
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()
    result = evaluate(args.dataset_root, args.checkpoint, args.output_root, args.batch_size)
    print(json.dumps({
        "sample_count": result["sample_count"],
        "accuracy": result["accuracy"],
        "macro_f1": result["macro_f1"],
        "output_root": args.output_root.as_posix(),
    }, indent=2))


if __name__ == "__main__":
    main()
