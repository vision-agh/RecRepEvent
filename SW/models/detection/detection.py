import torch
import lightning as L
import wandb
import numpy as np
import matplotlib.pyplot as plt

from typing import Dict, Tuple
import torch.nn as nn
from torch.nn.functional import softmax
from torchmetrics.functional.classification import accuracy
from torchmetrics import Accuracy
from torchmetrics.classification import ConfusionMatrix
from torchmetrics.detection.mean_ap import MeanAveragePrecision

from data.gen1.detection.gen1 import Gen1


from models.detection.utils.convert_bbox import convert_to_training_format
from models.detection.resnet import ResNetDetectionModel
from YOLOX.yolox.utils.ema import ModelEMA
from YOLOX.yolox.utils.lr_scheduler import LRScheduler

GEN1_CLASSES = {"car": 0, "pedestrian": 1}
GEN4_CLASSES = {0: "car", 1: "pedestrian", 2: "bicycle", 3: "motorcycle", 4: "bus", 5: "truck"}

class LNDetection(L.LightningModule):
    def __init__(self, config, train_dataloader_len=None):
        super().__init__()
        self.map = MeanAveragePrecision()

        if config["representation"] == "ToImage":
            self.model = ResNetDetectionModel(channels=2,
                                              num_classes=2)
        else:
            self.model = ResNetDetectionModel(channels=12,
                                              num_classes=2)
        self.ema_model = ModelEMA(self.model, 0.9998)

        self.save_hyperparameters()

        self.batch_size = config["batch_size"]
        self.num_classes = 2
        # --------------  training config --------------------- #
        # epoch number used for warmup
        self.warmup_epochs = 5
        # max training epoch
        self.max_epoch = 100
        # minimum learning rate during warmup
        self.warmup_lr = 0
        self.min_lr_ratio = 0.05
        # learning rate for one image. During training, lr will multiply batchsize.
        self.basic_lr_per_img = 0.01 / 64.0
        # name of LRScheduler
        self.scheduler = "yoloxwarmcos"
        # last #epoch to close augmention like mosaic
        self.no_aug_epochs = 97
        # apply EMA during training
        self.ema = True
        # weight decay of optimizer
        self.weight_decay = 5e-4
        # momentum of optimizer
        self.momentum = 0.9

        self.train_dataloader_len = train_dataloader_len

    def get_optimizer(self, batch_size):
        if self.warmup_epochs > 0:
            lr = 1
        else:
            lr = self.basic_lr_per_img * batch_size
        pg0, pg1, pg2 = [], [], []  # optimizer parameter groups
        for k, v in self.model.named_modules():
            if hasattr(v, "bias") and isinstance(v.bias, nn.Parameter):
                pg2.append(v.bias)  # biases
            if isinstance(v, nn.BatchNorm2d) or "bn" in k:
                pg0.append(v.weight)  # no decay
            elif hasattr(v, "weight") and isinstance(v.weight, nn.Parameter):
                pg1.append(v.weight)  # apply decay

        optimizer = torch.optim.SGD(
            pg0, lr=lr, momentum=self.momentum, nesterov=True
        )
        optimizer.add_param_group(
            {"params": pg1, "weight_decay": self.weight_decay}
        )  # add pg1 with weight_decay
        optimizer.add_param_group({"params": pg2})

        return optimizer
    
    def get_lr_scheduler(self, lr, iters_per_epoch):
        scheduler = LRScheduler(
            self.scheduler,
            lr,
            iters_per_epoch,
            self.max_epoch,
            warmup_epochs=self.warmup_epochs,
            warmup_lr_start=self.warmup_lr,
            no_aug_epochs=self.no_aug_epochs,
            min_lr_ratio=self.min_lr_ratio,
        )
        return scheduler

    def configure_optimizers(self):
        # 1. build optimizer
        optimizer = self.get_optimizer(self.batch_size)
        # 2. build your custom scheduler (no optimizer inside yet)
        custom_sched = self.get_lr_scheduler(
            lr=self.basic_lr_per_img * self.batch_size,
            iters_per_epoch=self.train_dataloader_len,
        )
        # 3. wrap it in a PyTorch LambdaLR
        torch_sched = torch.optim.lr_scheduler.LambdaLR(
            optimizer,
            lr_lambda=lambda step: custom_sched.update_lr(step)
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": torch_sched,
                "interval": "step",   # call .step() every optimizer.step()
                "frequency": 1,
            },
        }
    
    def configure_optimizers(self):
        # 1. build optimizer
        optimizer = self.get_optimizer(self.batch_size)
        # 2. build your custom scheduler (no optimizer inside yet)
        custom_sched = self.get_lr_scheduler(
            lr=self.basic_lr_per_img * self.batch_size,
            iters_per_epoch=self.train_dataloader_len,
        )
        # 3. wrap it in a PyTorch LambdaLR
        torch_sched = torch.optim.lr_scheduler.LambdaLR(
            optimizer,
            lr_lambda=lambda step: custom_sched.update_lr(step)
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": torch_sched,
                "interval": "step",   # call .step() every optimizer.step()
                "frequency": 1,
            },
        }

    def forward(self, model, data):
        target = convert_to_training_format(data['bboxes'].float(), data['batch_idx'], data['batch_idx'].max().item() + 1)
        x = model(data['representations'], target)
        return x

    def training_step(self, batch, batch_idx):
        outputs = self.forward(model=self.model,
                               data=batch)

        total_loss, iou_loss, l1_loss, conf_loss, cls_loss = outputs["total_loss"], outputs["iou_loss"], outputs["l1_loss"], outputs["conf_loss"], outputs["cls_loss"]
        self.log("train/total_loss", total_loss)
        self.log("train/iou_loss", iou_loss)
        self.log("train/l1_loss", l1_loss)
        self.log("train/conf_loss", conf_loss)
        self.log("train/cls_loss", cls_loss)
        return total_loss

    def on_before_backward(self, loss: torch.Tensor) -> None:
        if self.ema_model:
            self.ema_model.update(self.model)

    def validation_step(self, batch, batch_idx):
        preds = self.forward(model=self.ema_model.ema.to(batch['representations'].device),
                             data=batch)

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
        preds = self.forward(model=self.ema_model.ema.to(batch['representations'].device),
                             data=batch)
        gts = []
        unique_indices = batch["batch_idx"].unique(sorted=True)
        for idx in unique_indices:
            mask = (batch["batch_idx"] == idx)
            bbox = batch["bboxes"][mask].clone()
            bbox[:, 2:4] += bbox[:, :2]
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

        if self.test_pred:
            self.log_detections(self.test_pred)
            self.test_pred = None


    def log_detections(self, val_pred: dict) -> None:
        # Create 2d image from pos
        batch = val_pred['batch']
        gts = val_pred['gts']
        preds = val_pred['preds']
        ev_img = batch['representations']

        if ev_img.shape[1] > 2:
            ev_img = ev_img[:, :3, :, :]
        elif ev_img.shape[1] == 2:
            ev_img = torch.cat([ev_img, torch.zeros_like(ev_img)], dim=1)
            
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
