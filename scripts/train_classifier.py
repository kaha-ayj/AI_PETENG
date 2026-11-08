r"""Train a reproducible ResNet18 baseline for AI PETENG.

The script uses transfer learning and never reads the test split. For the
current 44-image dataset this is an experiment to verify the pipeline, not a
production-quality performance claim.

Usage:
    .venv\Scripts\python.exe scripts/train_classifier.py --epochs 5
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import torch
from sklearn.metrics import f1_score
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from app.models.cnn_classifier import (
    CLASS_NAMES,
    IMAGE_SIZE,
    ModelConfig,
    create_model,
    freeze_backbone,
    unfreeze_backbone,
)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def transforms_for_split():
    weights_transforms = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    )
    train = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(5),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.ToTensor(),
        weights_transforms,
    ])
    evaluation = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        weights_transforms,
    ])
    return train, evaluation


def run_epoch(model, loader, criterion, optimizer, device):
    training = optimizer is not None
    model.train(training)
    losses: list[float] = []
    actual: list[int] = []
    predicted: list[int] = []

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        if training:
            optimizer.zero_grad()
        with torch.set_grad_enabled(training):
            logits = model(images)
            loss = criterion(logits, labels)
            if training:
                loss.backward()
                optimizer.step()
        losses.append(float(loss.item()))
        actual.extend(labels.detach().cpu().tolist())
        predicted.extend(logits.argmax(dim=1).detach().cpu().tolist())

    return {
        "loss": sum(losses) / len(losses),
        "macro_f1": float(f1_score(actual, predicted, average="macro", zero_division=0)),
        "accuracy": sum(a == p for a, p in zip(actual, predicted)) / len(actual),
    }


def train(
    dataset_root: Path = Path("dataset"),
    weights_root: Path = Path("model_weights"),
    artifacts_root: Path = Path("artifacts"),
    epochs: int = 5,
    batch_size: int = 4,
    learning_rate: float = 1e-3,
    seed: int = 2026,
    freeze_epochs: int = 1,
) -> dict:
    seed_everything(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_transform, evaluation_transform = transforms_for_split()
    train_data = datasets.ImageFolder(dataset_root / "train", transform=train_transform)
    val_data = datasets.ImageFolder(dataset_root / "val", transform=evaluation_transform)

    if set(train_data.classes) != set(CLASS_NAMES) or set(val_data.classes) != set(CLASS_NAMES):
        raise ValueError(f"Kelas tidak sesuai: train={train_data.classes}, val={val_data.classes}")
    if train_data.class_to_idx != val_data.class_to_idx:
        raise ValueError("Mapping kelas train dan validation berbeda.")

    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=batch_size, shuffle=False)
    model = create_model(ModelConfig(pretrained=True)).to(device)
    freeze_backbone(model)
    class_counts = torch.bincount(torch.tensor(train_data.targets), minlength=len(CLASS_NAMES)).float()
    class_weights = (class_counts.sum() / (len(CLASS_NAMES) * class_counts)).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = AdamW((p for p in model.parameters() if p.requires_grad), lr=learning_rate)

    history = []
    best_f1 = -1.0
    best_state = None
    for epoch in range(1, epochs + 1):
        if epoch == freeze_epochs + 1:
            unfreeze_backbone(model)
            optimizer = AdamW(model.parameters(), lr=learning_rate * 0.1)
        train_metrics = run_epoch(model, train_loader, criterion, optimizer, device)
        val_metrics = run_epoch(model, val_loader, criterion, None, device)
        record = {"epoch": epoch, "train": train_metrics, "val": val_metrics}
        history.append(record)
        if val_metrics["macro_f1"] > best_f1:
            best_f1 = val_metrics["macro_f1"]
            best_state = {key: value.cpu() for key, value in model.state_dict().items()}

    weights_root.mkdir(parents=True, exist_ok=True)
    artifacts_root.mkdir(parents=True, exist_ok=True)
    checkpoint_path = weights_root / "resnet18-peteng-v1.pt"
    torch.save(best_state, checkpoint_path)
    (artifacts_root / "training_history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    metadata = {
        "model_version": "resnet18-peteng-v1",
        "architecture": "resnet18",
        "classes": list(CLASS_NAMES),
        "image_size": IMAGE_SIZE,
        "seed": seed,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "freeze_epochs": freeze_epochs,
        "device": str(device),
        "best_validation_macro_f1": best_f1,
    }
    (weights_root / "resnet18-peteng-v1.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--freeze-epochs", type=int, default=1)
    args = parser.parse_args()
    print(json.dumps(train(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        seed=args.seed,
        freeze_epochs=args.freeze_epochs,
    ), indent=2))


if __name__ == "__main__":
    main()
