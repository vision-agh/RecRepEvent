import numpy as np
import torch
import torch.nn as nn

from YOLOX.yolox.models.yolo_head import YOLOXHead
from YOLOX.yolox.models.losses import IOUloss
import torchvision

from torchvision.models import resnet18, resnet34, resnet50, resnet101, resnet152

def get_resnet(model_name='resnet18'):
    if model_name == 'resnet18':
        model = resnet18(weights=None)
    elif model_name == 'resnet34':
        model = resnet34(weights=None)
    elif model_name == 'resnet50':
        model = resnet50(weights=None)
    elif model_name == 'resnet101':
        model = resnet101(weights=None)
    elif model_name == 'resnet152':
        model = resnet152(weights=None)
    else:
        raise ValueError('Invalid model name: {}'.format(model_name))
    return model

def get_resnet_weights(model_name='resnet18'):
    if model_name == 'resnet18':
        weight = torchvision.models.resnet18(weights=True).state_dict()
    elif model_name == 'resnet34':
        weight = torchvision.models.resnet34(weights=True).state_dict()
    elif model_name == 'resnet50':
        weight = torchvision.models.resnet50(weights=True).state_dict()
    elif model_name == 'resnet101':
        weight = torchvision.models.resnet101(weights=True).state_dict()
    elif model_name == 'resnet152':
        weight = torchvision.models.resnet152(weights=True).state_dict()
    else:
        raise ValueError('Invalid model name: {}'.format(model_name))
    return weight

class DetectionBackbone(torch.nn.Module):
    def __init__(self, 
                 input_channels,
                 model_name='resnet18',
                 weights=None):
        super(DetectionBackbone, self).__init__()

        base_model = get_resnet(model_name)

        if weights:
            base_model.load_state_dict(get_resnet_weights(model_name))

        # Modyfikacja pierwszej warstwy, jeśli kanały wejściowe inne
        if input_channels != base_model.conv1.in_channels:
            base_model.conv1 = torch.nn.Conv2d(input_channels, base_model.conv1.out_channels, 
                                               kernel_size=base_model.conv1.kernel_size, 
                                               stride=base_model.conv1.stride, 
                                               padding=base_model.conv1.padding, 
                                               bias=False)

        # Rozdzielenie na etapy
        self.stem = torch.nn.Sequential(
            base_model.conv1,
            base_model.bn1,
            base_model.relu,
            base_model.maxpool
        )
        self.layer1 = base_model.layer1
        self.layer2 = base_model.layer2
        self.layer3 = base_model.layer3
        self.layer4 = base_model.layer4

    def forward(self, x):
        x = self.stem(x)
        out1 = self.layer1(x)
        out2 = self.layer2(out1)
        out3 = self.layer3(out2)
        out4 = self.layer4(out3)

        print(out1.shape, out2.shape, out3.shape, out4.shape)
        return out2, out3, out4


class ResNetDetectionModel(torch.nn.Module):
    
    def __init__(self, num_classes=2):
        super(ResNetDetectionModel, self).__init__()
        self.backbone = DetectionBackbone(12, 'resnet50', False)

        self.num_classes = num_classes
        self.conf_thre = 0.0001

        self.head = YOLOXHead(num_classes=num_classes, 
                                width=1,
                                strides=[7,14,28],
                                in_channels=[512, 1024, 2048])

    def forward(self, x, targets=None):
        backbone_outs = self.backbone(x)

        if self.training:
            assert targets is not None
            loss, iou_loss, conf_loss, cls_loss, l1_loss, num_fg = self.head(
                backbone_outs, targets)
            
            outputs = {
                "total_loss": loss,
                "iou_loss": iou_loss,
                "l1_loss": l1_loss,
                "conf_loss": conf_loss,
                "cls_loss": cls_loss,
                "num_fg": num_fg,
            }
        else:
            outputs = self.head(backbone_outs)
            outputs = self.postprocess_network_output(outputs, self.num_classes, height=224, width=224, filtering=True)

        return outputs

    def visualize(self, x, targets, save_prefix="assign_vis_"):
        fpn_outs = self.backbone(x)
        self.head.visualize_assign_result(fpn_outs, targets, x, save_prefix)

    def postprocess_network_output(self, prediction, num_classes, conf_thre=0.001, nms_thre=0.65, height=640, width=640, filtering=True):
        prediction[..., :2] -= prediction[...,2:4] / 2 # cxcywh->xywh
        prediction[..., 2:4] += prediction[...,:2]

        # print(prediction[:,4])
        output = []
        for i, image_pred in enumerate(prediction):

            # If none are remaining => process next image
            if len(image_pred) == 0:
                output.append({
                    "boxes": torch.zeros(0, 4, dtype=torch.float32, device='cpu'),
                    "scores": torch.zeros(0, dtype=torch.float, device='cpu'),
                    "labels": torch.zeros(0, dtype=torch.long, device='cpu')
                })
                continue
            
            # Get score and class with highest confidence
            class_conf, class_pred = torch.max(image_pred[:, 5: 5 + num_classes], 1, keepdim=True)

            image_pred_copy = image_pred.clone()
            image_pred_copy[:, 4:5] *= class_conf

            conf_mask = (image_pred_copy[:, 4] * class_conf.squeeze() >= self.conf_thre).squeeze()
            # Detections ordered as (x1, y1, x2, y2, obj_conf, class_conf, class_pred)
            detections = torch.cat((image_pred_copy[:, :5], class_pred), 1)

            if filtering:
                detections = detections[conf_mask]

            if len(detections) == 0:
                output.append({
                    "boxes": torch.zeros(0, 4, dtype=torch.float32, device='cpu'),
                    "scores": torch.zeros(0, dtype=torch.float, device='cpu'),
                    "labels": torch.zeros(0, dtype=torch.long, device='cpu')
                })
                continue

            nms_out_index = self.batched_nms_coordinate_trick(detections[:, :4], detections[:, 4], detections[:, 5],
                                                        nms_thre, width=width, height=height)

            if filtering:
                detections = detections[nms_out_index]

            # print(detections[:,4])
            output.append({
                "boxes": detections[:, :4].to('cpu'),
                "scores": detections[:, 4].to('cpu'),
                "labels": detections[:, -1].long().to('cpu')
            })

        return output

    def batched_nms_coordinate_trick(self, boxes, scores, idxs, iou_threshold, width, height):
        # adopted from torchvision nms, but faster
        if boxes.numel() == 0:
            return torch.empty((0,), dtype=torch.int64, device=boxes.device)
        max_dim = max([width, height])
        offsets = idxs * float(max_dim + 1)
        boxes_for_nms = boxes + offsets[:, None]
        keep = torchvision.ops.nms(boxes_for_nms, scores, iou_threshold)
        return keep