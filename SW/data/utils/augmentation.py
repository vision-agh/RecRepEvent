import torch
import cv2
import numpy as np

import torchvision.transforms as transforms

class RandomHFlip:
    def __init__(self, cfg):
        cfg_flip = cfg.augmentation.h_flip
        self.p = cfg_flip.p

        self.width = cfg.image_size.W
        self.height  = cfg.image_size.H

    def __call__(self, img, bbox):
        if torch.rand(1) < self.p:
            img = transforms.functional.hflip(img)
            if bbox:
                bbox = self.width - 1 - (bbox[:, 0] + bbox[:, 2])
        return img, bbox
    

import math
import random

import torch
import torch.nn.functional as F
import torchvision.transforms.functional as TF


def _zoom(img: torch.Tensor,
          bboxes: torch.Tensor,
          scale: float) -> (torch.Tensor, torch.Tensor):
    """
    Zoom in (>1) via center‐crop, or zoom out (<1) via padding,
    then resize back to original H×W.
    bboxes are in (x, y, w, h) format.
    """
    C, H, W = img.shape
    # 1) scale the image
    x = img.unsqueeze(0)  # 1×C×H×W
    x = F.interpolate(x,
                      scale_factor=scale,
                      mode='bilinear',
                      align_corners=False)[0]
    C2, H2, W2 = x.shape

    # 2) crop or pad to H×W
    if scale >= 1:
        # center‐crop H×W
        top = (H2 - H) // 2
        left = (W2 - W) // 2
        img2 = x[:, top:top+H, left:left+W]
        dx, dy = -left, -top
    else:
        # pad to H×W
        pad_h = H - H2
        pad_w = W - W2
        top = pad_h // 2
        left = pad_w // 2
        img2 = F.pad(x, (left, pad_w-left, top, pad_h-top))
        dx, dy = left, top

    # 3) adjust bboxes
    # scale centres & sizes, then shift
    boxes2 = bboxes.clone().float()
    boxes2[:, :2] = boxes2[:, :2] * scale + torch.tensor([dx, dy], device=img.device)
    boxes2[:, 2:] = boxes2[:, 2:] * scale
    return img2, boxes2


class RandomZoom:
    def __init__(self,
                 scale_min: float = 0.8,
                 scale_max: float = 1.2,
                 p: float = 0.5):
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.p = p

    def __call__(self, img: torch.Tensor, bboxes: torch.Tensor):
        if random.random() < self.p:
            f = random.uniform(self.scale_min, self.scale_max)
            return _zoom(img, bboxes, f)
        return img, bboxes


def _get_affine_matrix(params, center):
    """
    Build a 3×3 homogeneous matrix from torchvision-style params:
    angle (deg), translate (tx, ty), scale, shear (sx, sy).
    """
    angle, (tx, ty), scale, (shear_x, shear_y) = params
    cx, cy = center

    # Convert to radians
    a = math.radians(angle)
    sx = math.radians(shear_x)
    sy = math.radians(shear_y)

    # Rotation + scale
    R = torch.tensor([
        [ math.cos(a)*scale, -math.sin(a)*scale, 0],
        [ math.sin(a)*scale,  math.cos(a)*scale, 0],
        [                0,                 0, 1]
    ], dtype=torch.float32)

    # Shear
    Sh = torch.tensor([
        [1, -math.tan(sy), 0],
        [-math.tan(sx), 1, 0],
        [0, 0, 1]
    ], dtype=torch.float32)

    # Translations
    T1 = torch.tensor([
        [1, 0, -cx],
        [0, 1, -cy],
        [0, 0,   1]
    ], dtype=torch.float32)
    T2 = torch.tensor([
        [1, 0, cx + tx],
        [0, 1, cy + ty],
        [0, 0,     1]
    ], dtype=torch.float32)

    # full = T2 @ R @ Sh @ T1
    return T2 @ R @ Sh @ T1


def _affine_bboxes(bboxes: torch.Tensor,
                   matrix: torch.Tensor) -> torch.Tensor:
    """
    Apply a 3×3 homography to each bbox's four corners,
    then return new axis‐aligned boxes (x,y,w,h).
    """
    # bboxes: N×4 in (x,y,w,h)
    N = bboxes.size(0)
    # corners: 4 corners each -> (4N)×3
    corners = []
    for x, y, w, h in bboxes:
        corners += [
            [x,     y,     1.],
            [x + w, y,     1.],
            [x + w, y + h, 1.],
            [x,     y + h, 1.]
        ]
    corners = torch.tensor(corners, device=bboxes.device)  # (4N,3)
    # transform
    trans = (matrix @ corners.t()).t()                    # (4N,3)
    trans = trans[:, :2] / trans[:, 2:3]                  # normalize

    # reshape back to N×4 corners
    trans = trans.view(N, 4, 2)
    x_min, _ = trans[:,:,0].min(dim=1)
    y_min, _ = trans[:,:,1].min(dim=1)
    x_max, _ = trans[:,:,0].max(dim=1)
    y_max, _ = trans[:,:,1].max(dim=1)

    out = torch.stack([x_min, y_min,
                       x_max - x_min,
                       y_max - y_min], dim=1)
    return out


class RandomAffine:
    def __init__(self,
                 degrees: float = 10,
                 translate: tuple = (0.1, 0.1),
                 scale: tuple = (0.9, 1.1),
                 shear: tuple = (5.0, 5.0),
                 p: float = 0.5):
        self.degrees = degrees
        self.translate = translate
        self.scale = scale
        self.shear = (shear, shear)
        self.p = p

    def __call__(self, img: torch.Tensor, bboxes: torch.Tensor):
        if random.random() < self.p:
            C, H, W = img.shape
            params = transforms.RandomAffine.get_params(
                degrees=(-self.degrees, self.degrees),
                translate=self.translate,
                scale_ranges=self.scale,
                shears=self.shear,
                img_size=(H, W)
            )
            # warp image
            img2 = TF.affine(img, *params, resample=F.InterpolationMode.BILINEAR)
            # compute and apply homography on bboxes
            M = _get_affine_matrix(params, center=(W*0.5, H*0.5)).to(img.device)
            bb2 = _affine_bboxes(bboxes, M)
            return img2, bb2
        return img, bboxes


class MixUp:
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha

    def __call__(self,
                 sample1: tuple[torch.Tensor, torch.Tensor],
                 sample2: tuple[torch.Tensor, torch.Tensor]
                 ) -> tuple[torch.Tensor, torch.Tensor, float]:
        """
        sample1 = (img1, bboxes1)
        sample2 = (img2, bboxes2)
        returns mixed_img, mixed_bboxes, lambda
        """
        img1, bb1 = sample1
        img2, bb2 = sample2
        lam = np.random.beta(self.alpha, self.alpha)

        img = lam * img1 + (1 - lam) * img2
        # simply concatenate both sets of boxes
        bboxes = torch.cat([bb1, bb2], dim=0)

        return img, bboxes, lam
