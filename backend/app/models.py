import os
import logging

import torch
import torch.nn as nn
from torchvision import models, transforms

logger = logging.getLogger("brain_stroke_agent")

CLASS_NAMES = ["Bleeding", "Ischemia", "Normal"]

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

val_transform = transforms.Compose(
    [
        transforms.Lambda(lambda img: img.convert("RGB") if img.mode != "RGB" else img),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


class CNNModel(nn.Module):
    """Custom CNN — identical architecture to the training notebook."""

    def __init__(self, num_classes: int = 3):
        super().__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Sequential(
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.gap(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


def _weight_path(model_dir: str, filename: str) -> str:
    path = os.path.join(model_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing model weight file: {path}. "
            "Place cnn_model.pth, resnet18_model.pth, alexnet_model.pth in MODEL_DIR."
        )
    return path


def load_models(model_dir: str):
    """Loads the 3 trained models exactly as in the notebook. Returns a dict."""
    cnn = CNNModel(num_classes=3)
    cnn.load_state_dict(torch.load(_weight_path(model_dir, "cnn_model.pth"), map_location=DEVICE))
    cnn.to(DEVICE).eval()

    resnet = models.resnet18(weights=None)
    resnet.fc = nn.Linear(resnet.fc.in_features, 3)
    resnet.load_state_dict(torch.load(_weight_path(model_dir, "resnet18_model.pth"), map_location=DEVICE))
    resnet.to(DEVICE).eval()

    alexnet = models.alexnet(weights=None)
    alexnet.classifier[6] = nn.Linear(4096, 3)
    alexnet.load_state_dict(torch.load(_weight_path(model_dir, "alexnet_model.pth"), map_location=DEVICE))
    alexnet.to(DEVICE).eval()

    logger.info("All 3 models loaded on device=%s", DEVICE)
    return {"CNN": cnn, "ResNet18": resnet, "AlexNet": alexnet}


def get_target_layer(model: nn.Module, model_name: str):
    if model_name == "CNN":
        return model.layer2[0]
    if model_name == "ResNet18":
        return model.layer4[-1].conv2
    if model_name == "AlexNet":
        for layer in reversed(model.features):
            if isinstance(layer, nn.Conv2d):
                return layer
    raise ValueError(f"No target conv layer defined for {model_name}")
