import torch
from models.detection.resnet import resnet


backbone = resnet(
                pretrained=None,
                version="50",
                channels=12,
            )

# print(backbone)

img = torch.rand(1, 12, 224, 224)


for out in backbone(img):
    print(out.shape)