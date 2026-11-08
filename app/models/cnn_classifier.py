from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
from torchvision.models import ResNet18_Weights, resnet18


CLASS_NAMES = ("bukan_jalan", "gelap", "redup", "terang")
IMAGE_SIZE = 224


@dataclass(frozen=True)
class ModelConfig:
    model_name: str = "resnet18"
    num_classes: int = len(CLASS_NAMES)
    pretrained: bool = True


def create_model(config: ModelConfig | None = None) -> nn.Module:
    config = config or ModelConfig()
    if config.model_name != "resnet18":
        raise ValueError(f"Model tidak didukung: {config.model_name}")

    weights = ResNet18_Weights.DEFAULT if config.pretrained else None
    model = resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, config.num_classes)
    return model


def freeze_backbone(model: nn.Module) -> None:
    for parameter in model.parameters():
        parameter.requires_grad = False
    for parameter in model.fc.parameters():
        parameter.requires_grad = True


def unfreeze_backbone(model: nn.Module) -> None:
    for parameter in model.parameters():
        parameter.requires_grad = True
