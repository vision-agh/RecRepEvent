import h5py
import numpy as np
import torch
import torchvision.transforms as transforms

from utils.pack_events import pack_events_parallel


class EventDatasetRepresentation(torch.utils.data.Dataset):
    def __init__(self, filepath: str, 
                        cfg,
                        augment: bool = False):
        """
        Expects your .h5 to contain:
          - events         : (total_events, 4) float32
          - bboxes         : (total_bboxes, 5) int32
          - events_splits  : (num_samples+1,) int64
          - bboxes_splits  : (num_samples+1,) int64
        """
        self.filepath = filepath
        self.cfg = cfg

        # read just the splits so we know how many samples and where each lives
        with h5py.File(self.filepath, "r") as f:
            self.events_splits = f["rep_splits"][:]      # e.g. [0, 100, 250, ...]
            self.bboxes_splits = f["bboxes_splits"][:]
        self.num_samples = len(self.events_splits) - 1

        # Will open the file & datasets once per worker
        self._h5f    = None
        self._ds_ev  = None
        self._ds_bb  = None

    def __len__(self):
        return self.num_samples
    
    def get_sample(self, idx):
        # lazily open
        if self._h5f is None:
            self._h5f   = h5py.File(self.filepath, "r")
            self._ds_ev = self._h5f["representations"]
            self._ds_bb = self._h5f["bboxes"]

        # figure out our slice in the flat arrays
        e_start = int(self.events_splits[idx])
        e_end   = int(self.events_splits[idx+1])
        b_start = int(self.bboxes_splits[idx])
        b_end   = int(self.bboxes_splits[idx+1])

        # pull out just our events & bboxes
        ev_np = self._ds_ev[e_start:e_end]      # shape = (n_ev, 4)
        bb_np = self._ds_bb[b_start:b_end]      # shape = (n_bb, 5)
        return ev_np, bb_np


    def __getitem__(self, idx):
        ev_np, bb_np = self.get_sample(idx)
        rep = torch.from_numpy(ev_np)
        bbox = torch.from_numpy(bb_np).float()

        rep = transforms.Resize((224, 224))(rep)

        bbox[:, 0] *= 224 / 304  # x1
        bbox[:, 1] *= 224 / 240 # y1
        bbox[:, 2] *= 224 / 304  # x2
        bbox[:, 3] *= 224 / 240 # y2
        return rep, bbox

<<<<<<< HEAD
=======



###################################################################################################
###################################################################################################
###################################################################################################

import random
import cv2
import numpy as np

from YOLOX.yolox.data.data_augment import random_affine
from YOLOX.yolox.utils import adjust_box_anns, get_local_rank
from YOLOX.yolox.data.datasets.datasets_wrapper import Dataset
from YOLOX.yolox.data.datasets.mosaicdetection import MosaicDetection

def get_mosaic_coordinate(mosaic_image, mosaic_index, xc, yc, w, h, input_h, input_w):
    # TODO update doc
    # index0 to top left part of image
    if mosaic_index == 0:
        x1, y1, x2, y2 = max(xc - w, 0), max(yc - h, 0), xc, yc
        small_coord = w - (x2 - x1), h - (y2 - y1), w, h
    # index1 to top right part of image
    elif mosaic_index == 1:
        x1, y1, x2, y2 = xc, max(yc - h, 0), min(xc + w, input_w * 2), yc
        small_coord = 0, h - (y2 - y1), min(w, x2 - x1), h
    # index2 to bottom left part of image
    elif mosaic_index == 2:
        x1, y1, x2, y2 = max(xc - w, 0), yc, xc, min(input_h * 2, yc + h)
        small_coord = w - (x2 - x1), 0, w, min(y2 - y1, h)
    # index2 to bottom right part of image
    elif mosaic_index == 3:
        x1, y1, x2, y2 = xc, yc, min(xc + w, input_w * 2), min(input_h * 2, yc + h)  # noqa
        small_coord = 0, 0, min(w, x2 - x1), min(y2 - y1, h)
    return (x1, y1, x2, y2), small_coord


class TrainDataloader(MosaicDetection):
    def __init__(self, 
                 dataset, img_size, mosaic=False, preproc=None, 
                 degrees=0.373, translate=0.245, mosaic_scale=(0.8, 1.2), 
                 mixup_scale=(0.9, 1.1), shear=0.602, enable_mixup=True, 
                 mosaic_prob=1.0, mixup_prob=0.243, *args):
        super().__init__(dataset, img_size, mosaic, preproc, 
                         degrees, translate, mosaic_scale, 
                         mixup_scale, shear, enable_mixup, 
                         mosaic_prob, mixup_prob, *args)
        
        self.filepath = dataset
        with h5py.File(self.filepath, "r") as f:
            self.events_splits = f["rep_splits"][:]      # e.g. [0, 100, 250, ...]
            self.bboxes_splits = f["bboxes_splits"][:]
        self.num_samples = len(self.events_splits) - 1

        # Will open the file & datasets once per worker
        self._h5f    = None
        self._ds_ev  = None
        self._ds_bb  = None

    def __len__(self):
        return self.num_samples
    
    def get_sample(self, idx):
        # lazily open
        if self._h5f is None:
            self._h5f   = h5py.File(self.filepath, "r")
            self._ds_ev = self._h5f["representations"]
            self._ds_bb = self._h5f["bboxes"]

        # figure out our slice in the flat arrays
        e_start = int(self.events_splits[idx])
        e_end   = int(self.events_splits[idx+1])
        b_start = int(self.bboxes_splits[idx])
        b_end   = int(self.bboxes_splits[idx+1])

        # pull out just our events & bboxes
        ev_np = self._ds_ev[e_start:e_end]      # shape = (n_ev, 4)
        bb_np = self._ds_bb[b_start:b_end]      # shape = (n_bb, 5)

        bb_np = bb_np.astype(np.float32)
        ev_np = ev_np.transpose(1, 2, 0)
        ev_np -= ev_np.min()
        ev_np = ev_np / ev_np.max() * 255.0
        # labels to xyxy format
        bb_np[:, 2] = bb_np[:, 0] + bb_np[:, 2]
        bb_np[:, 3] = bb_np[:, 1] + bb_np[:, 3]
        
        return ev_np, bb_np

    
    @Dataset.mosaic_getitem
    def __getitem__(self, idx):
        if self.enable_mosaic and random.random() < self.mosaic_prob:
            mosaic_labels = []
            input_h, input_w = self.input_dim

            # yc, xc = s, s  # mosaic center x, y
            yc = int(random.uniform(0.5 * input_h, 1.5 * input_h))
            xc = int(random.uniform(0.5 * input_w, 1.5 * input_w))

            # 3 additional image indices
            indices = [idx] + [random.randint(0, self.num_samples) for _ in range(3)]

            for i_mosaic, index in enumerate(indices):
                img, _labels = self.get_sample(index)
                h0, w0 = img.shape[:2]  # orig hw
                scale = min(1. * input_h / h0, 1. * input_w / w0)
                img = cv2.resize(
                    img, (int(w0 * scale), int(h0 * scale)), interpolation=cv2.INTER_LINEAR
                )
                # generate output mosaic image
                (h, w, c) = img.shape[:3]
                if i_mosaic == 0:
                    mosaic_img = np.full((input_h * 2, input_w * 2, c), 114, dtype=np.uint8)

                # suffix l means large image, while s means small image in mosaic aug.
                (l_x1, l_y1, l_x2, l_y2), (s_x1, s_y1, s_x2, s_y2) = get_mosaic_coordinate(
                    mosaic_img, i_mosaic, xc, yc, w, h, input_h, input_w
                )

                mosaic_img[l_y1:l_y2, l_x1:l_x2] = img[s_y1:s_y2, s_x1:s_x2]
                padw, padh = l_x1 - s_x1, l_y1 - s_y1

                labels = _labels.copy()
                # Normalized xywh to pixel xyxy format
                if _labels.size > 0:
                    labels[:, 0] = scale * _labels[:, 0] + padw
                    labels[:, 1] = scale * _labels[:, 1] + padh
                    labels[:, 2] = scale * _labels[:, 2] + padw
                    labels[:, 3] = scale * _labels[:, 3] + padh
                mosaic_labels.append(labels)

            if len(mosaic_labels):
                mosaic_labels = np.concatenate(mosaic_labels, 0)
                np.clip(mosaic_labels[:, 0], 0, 2 * input_w, out=mosaic_labels[:, 0])
                np.clip(mosaic_labels[:, 1], 0, 2 * input_h, out=mosaic_labels[:, 1])
                np.clip(mosaic_labels[:, 2], 0, 2 * input_w, out=mosaic_labels[:, 2])
                np.clip(mosaic_labels[:, 3], 0, 2 * input_h, out=mosaic_labels[:, 3])

            mosaic_img, mosaic_labels = random_affine(
                mosaic_img,
                mosaic_labels,
                target_size=(input_w, input_h),
                degrees=self.degrees,
                translate=self.translate,
                scales=self.scale,
                shear=self.shear,
            )

            # -----------------------------------------------------------------
            # CopyPaste: https://arxiv.org/abs/2012.07177
            # -----------------------------------------------------------------
            if (
                self.enable_mixup
                and not len(mosaic_labels) == 0
                and random.random() < self.mixup_prob
            ):
                mosaic_img, mosaic_labels = self.mixup(mosaic_img, mosaic_labels, self.input_dim)
            mix_img, padded_labels = self.preproc(mosaic_img, mosaic_labels, self.input_dim)

            # -----------------------------------------------------------------
            # img_info and img_id are not used for training.
            # They are also hard to be specified on a mosaic image.
            # -----------------------------------------------------------------

            mix_img = torch.from_numpy(mix_img).float()
            padded_labels = torch.from_numpy(padded_labels).float()
            return mix_img, padded_labels

        else:
            img, label = self.get_sample(idx)
            img, label = self.preproc(img, label, self.input_dim)
            img = torch.from_numpy(img).float()
            label = torch.from_numpy(label).float()
            return img, label
        
    def mixup(self, origin_img, origin_labels, input_dim):
        jit_factor = random.uniform(*self.mixup_scale)
        FLIP = random.uniform(0, 1) > 0.5
        cp_labels = []
        while len(cp_labels) == 0:
            cp_index = random.randint(0, self.__len__() - 1)
            _, cp_labels = self.get_sample(cp_index)
        img, cp_labels = self.get_sample(cp_index)

        if len(img.shape) == 3:
            cp_img = np.ones((input_dim[0], input_dim[1], 12), dtype=np.uint8) * 114
        else:
            cp_img = np.ones(input_dim, dtype=np.uint8) * 114

        cp_scale_ratio = min(input_dim[0] / img.shape[0], input_dim[1] / img.shape[1])
        resized_img = cv2.resize(
            img,
            (int(img.shape[1] * cp_scale_ratio), int(img.shape[0] * cp_scale_ratio)),
            interpolation=cv2.INTER_LINEAR,
        )

        cp_img[
            : int(img.shape[0] * cp_scale_ratio), : int(img.shape[1] * cp_scale_ratio)
        ] = resized_img

        cp_img = cv2.resize(
            cp_img,
            (int(cp_img.shape[1] * jit_factor), int(cp_img.shape[0] * jit_factor)),
        )
        cp_scale_ratio *= jit_factor

        if FLIP:
            cp_img = cp_img[:, ::-1, :]

        origin_h, origin_w = cp_img.shape[:2]
        target_h, target_w = origin_img.shape[:2]
        padded_img = np.zeros(
            (max(origin_h, target_h), max(origin_w, target_w), 12), dtype=np.uint8
        )
        padded_img[:origin_h, :origin_w] = cp_img

        x_offset, y_offset = 0, 0
        if padded_img.shape[0] > target_h:
            y_offset = random.randint(0, padded_img.shape[0] - target_h - 1)
        if padded_img.shape[1] > target_w:
            x_offset = random.randint(0, padded_img.shape[1] - target_w - 1)
        padded_cropped_img = padded_img[
            y_offset: y_offset + target_h, x_offset: x_offset + target_w
        ]

        cp_bboxes_origin_np = adjust_box_anns(
            cp_labels[:, :4].copy(), cp_scale_ratio, 0, 0, origin_w, origin_h
        )
        if FLIP:
            cp_bboxes_origin_np[:, 0::2] = (
                origin_w - cp_bboxes_origin_np[:, 0::2][:, ::-1]
            )
        cp_bboxes_transformed_np = cp_bboxes_origin_np.copy()
        cp_bboxes_transformed_np[:, 0::2] = np.clip(
            cp_bboxes_transformed_np[:, 0::2] - x_offset, 0, target_w
        )
        cp_bboxes_transformed_np[:, 1::2] = np.clip(
            cp_bboxes_transformed_np[:, 1::2] - y_offset, 0, target_h
        )

        cls_labels = cp_labels[:, 4:5].copy()
        box_labels = cp_bboxes_transformed_np
        labels = np.hstack((box_labels, cls_labels))
        origin_labels = np.vstack((origin_labels, labels))
        origin_img = origin_img.astype(np.float32)
        origin_img = 0.5 * origin_img + 0.5 * padded_cropped_img.astype(np.float32)

        return origin_img.astype(np.uint8), origin_labels
>>>>>>> ddd3e44 (update HW files)
