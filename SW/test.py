import argparse

from omegaconf import OmegaConf
from models.detection.resnet import ResNetDetectionModel



cfg = OmegaConf.create({
    "channels": 3,
    "num_classes": 2,
    "weights": None})

print(cfg)