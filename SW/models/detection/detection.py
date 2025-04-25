import torch
import lightning as L
import wandb
import numpy as np
import matplotlib.pyplot as plt

from torchmetrics.functional.classification import accuracy
from torchmetrics import Accuracy
from torchmetrics.classification import ConfusionMatrix

from typing import Dict, Tuple
from torch.nn.functional import softmax

from torchmetrics.detection.mean_ap import MeanAveragePrecision


from models.detection.utils.convert_bbox import convert_to_training_format

from models.detection.resnet import ResNetDetectionModel

GEN1_CLASSES = {"car": 0, "pedestrian": 1}
GEN4_CLASSES = {0: "car", 1: "pedestrian", 2: "bicycle", 3: "motorcycle", 4: "bus", 5: "truck"}

class LNDetection(L.LightningModule):
    def __init__(self, cfg_dataset):
        super().__init__()
        self.lr = 0.0001
        self.weight_decay = 0.001

        self.batch_size = 16
        self.num_classes = 2

        self.map = MeanAveragePrecision()
        self.model = ResNetDetectionModel(num_classes=2)

        self.save_hyperparameters()

        self.val_pred = None
        self.train_pred = None
        self.pred = []
        self.target = []

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.lr, weight_decay=self.weight_decay)
        return optimizer

    def forward(self, data):  
        target = convert_to_training_format(data['bboxes'].float(), data['batch_idx'], self.batch_size)
        x = self.model(data['representations'], target)
        return x

    def training_step(self, batch, batch_idx):
        outputs = self.forward(data=batch)

        total_loss, iou_loss, l1_loss, conf_loss, cls_loss = outputs["total_loss"], outputs["iou_loss"], outputs["l1_loss"], outputs["conf_loss"], outputs["cls_loss"]
        self.log("train/total_loss", total_loss)
        self.log("train/iou_loss", iou_loss)
        self.log("train/l1_loss", l1_loss)
        self.log("train/conf_loss", conf_loss)
        self.log("train/cls_loss", cls_loss)

        return total_loss

    def validation_step(self, batch, batch_idx):
        preds = self.forward(data=batch)

        gts = []
        unique_indices = batch["batch_idx"].unique(sorted=True)
        for idx in unique_indices:
            mask = (batch["batch_idx"] == idx)
            bbox = batch["bboxes"][mask].clone()
            bbox[:, 2:4] += bbox[:, :2]  # zamiana z xywh na xyxy
            gts.append({
                "boxes": bbox[:, :4].cpu(),
                "labels": bbox[:, 4].cpu().long()
            })

        self.map.update(preds, gts)

        self.val_pred = {'batch': batch,
                         'gts': gts, 
                         'preds': preds}
        
    def on_validation_epoch_end(self) -> None:
        maps = self.map.compute()
        self.log("val/mAP", maps['map'])
        self.log("val/mAP50", maps['map_50'])
        self.log("val/mAP75", maps['map_75'])
        self.map.reset()
        
        if self.val_pred:
            self.log_detections(self.val_pred)
            self.val_pred = None
    
    def test_step(self, batch, batch_idx):
        preds = self.forward(data=batch)

        gts = []
        unique_indices = batch["batch_idx"].unique(sorted=True)
        for idx in unique_indices:
            mask = (batch["batch_idx"] == idx)
            bbox = batch["bboxes"][mask].clone()
            bbox[:, 2:4] += bbox[:, :2]  # zamiana z xywh na xyxy
            gts.append({
                "boxes": bbox[:, :4].cpu(),
                "labels": bbox[:, 4].cpu().long()
            })

        self.map.update(preds, gts)

        self.test_pred = {'batch': batch,
                         'gts': gts, 
                         'preds': preds}
        
    def on_test_epoch_end(self) -> None:
        maps = self.map.compute()
        self.log("test/mAP", maps['map'])
        self.log("test/mAP50", maps['map_50'])
        self.log("test/mAP75", maps['map_75'])
        self.map.reset()

    def log_detections(self, val_pred: dict) -> None:
        # Create 2d image from pos
        batch = val_pred['batch']

        gts = val_pred['gts']
        preds = val_pred['preds']
        ev_img = batch['representations']

        if ev_img.shape[1] > 2:
            ev_img = ev_img[:, :3, :, :]
            
        class_id_to_label = {int(v): k for k, v in GEN1_CLASSES.items()}

        images = []

        # Iterate over the first four batches
        for i in range(batch['batch_idx'].max().item() + 1):
            bbs = preds[i]['boxes'].cpu().numpy()
            labels = preds[i]['labels'].cpu().numpy()
            scores = preds[i]['scores'].cpu().numpy()

            pred_all_boxes = []
            gt_all_boxes = []
            for bb, label, score in zip(bbs, labels, scores):
                x1, y1, x2, y2 = bb
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                box_data = {
                    'position': {'minX': x1, 'minY': y1, 'maxX': x2, 'maxY': y2},
                    'class_id': int(label),
                    'box_caption': f'{label} {score:.2f}',
                    'scores': {'score': float(score)},
                    'domain': 'pixel'
                }
                pred_all_boxes.append(box_data)

            for bb, label in zip(gts[i]['boxes'], gts[i]['labels']):
                x1, y1, x2, y2 = bb
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                box_data = {
                    'position': {'minX': x1, 'minY': y1, 'maxX': x2, 'maxY': y2},
                    'class_id': int(label.cpu().item()),
                    'box_caption': f'{label.cpu().item()}',
                    'scores': {'score': 1.0},
                    'domain': 'pixel'
                }
                gt_all_boxes.append(box_data)

            # Add the image with bounding boxes to the list
            images.append(
                wandb.Image(ev_img[i], boxes={
                    'predictions': {
                        'box_data': pred_all_boxes,
                        'class_labels': class_id_to_label
                    },
                    'ground_truth': {
                        'box_data': gt_all_boxes,
                        'class_labels': class_id_to_label
                    }
                })
            )

        # Log all images under a single log key
        self.logger.experiment.log({'val/predictions': images})
