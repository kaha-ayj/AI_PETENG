import torch

from app.models.cnn_classifier import CLASS_NAMES, ModelConfig, create_model, freeze_backbone


def test_create_model_has_four_output_classes():
    model = create_model(ModelConfig(pretrained=False))
    output = model(torch.randn(2, 3, 224, 224))

    assert tuple(output.shape) == (2, len(CLASS_NAMES))


def test_freeze_backbone_keeps_classifier_trainable():
    model = create_model(ModelConfig(pretrained=False))
    freeze_backbone(model)

    assert all(not parameter.requires_grad for name, parameter in model.named_parameters() if not name.startswith("fc."))
    assert all(parameter.requires_grad for name, parameter in model.named_parameters() if name.startswith("fc."))
