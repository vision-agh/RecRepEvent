import os
import gc
from pathlib import Path

import numpy as np
import h5py
import lightning as L
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from data.gen1.detection.base import EventDatasetRepresentation
from representations.get_representation import get_item_transform
from models.recurrent.encoder import Encoder

from data.gen1.detection.utils.mosaicdetection import MosaicDetection
from data.gen1.detection.utils.data_augment import TrainTransform

class Gen1(L.LightningDataModule):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        # directory where we save the processed HDF5s
        self.save_dir = os.path.join(cfg["dir_to_save"], cfg["representation"])
        # representation dimensions (fallback to original defaults)
        self.height = cfg.get("height", 240)
        self.width = cfg.get("width", 304)

        if cfg["representation"] == "ToImage":
            self.img_size = (224, 224, 2)
        else:
            self.img_size = (224, 224, 12)

    def prepare_data(self):
        os.makedirs(self.save_dir, exist_ok=True)
        encoder = None
        if self.cfg["representation"] == "Encoder":
            encoder = Encoder(
                input_size=2,
                hidden_size=12,
                num_bits=8,
                input_num_bits=12,
            ).eval().cuda()
            encoder.compile()
            checkpoint = torch.load(self.cfg["encoder_checkpoint"], weights_only=True)
            encoder_weights = {k.replace("encoder.", ""): v for k, v in checkpoint["state_dict"].items() if k.startswith("encoder.")}
            encoder.load_state_dict(encoder_weights, strict=False)

        for split in ["train", "val", "test"]:
            input_path = os.path.join(self.cfg["dir_to_save"], f"{split}.h5")
            output_path = os.path.join(self.save_dir, f"{split}.h5")
            if os.path.exists(output_path):
                continue

            # Open input and output files
            with h5py.File(input_path, "r") as in_h5, \
                h5py.File(output_path, "w") as out_h5:
                # read original splits
                ev_splits = in_h5["events_splits"][:]
                bboxes_splits = in_h5["bboxes_splits"][:]
                ds_ev_full = in_h5["events"]
                ds_bb_full = in_h5["bboxes"]

                # create empty, resizable datasets in output
                rep_ds = out_h5.create_dataset(
                    "representations",
                    shape=(0, self.height, self.width),
                    maxshape=(None, self.height, self.width),
                    dtype="float32",
                    chunks=(1, self.height, self.width),
                )
                bboxes_ds = out_h5.create_dataset(
                    "bboxes",
                    shape=(0, 5),
                    maxshape=(None, 5),
                    dtype="int32",
                    chunks=(1024, 5),
                )

                rep_lengths = []
                bbox_lengths = []
                idx_r = 0
                idx_b = 0

                for i in tqdm(range(len(ev_splits) - 1), desc=f"Processing {split}"):
                    # slice event and bbox ranges
                    e_start, e_end = ev_splits[i], ev_splits[i + 1]
                    b_start, b_end = bboxes_splits[i], bboxes_splits[i + 1]
                    ev_np = ds_ev_full[e_start:e_end]
                    bb_np = ds_bb_full[b_start:b_end]

                    # convert to structured array for the transform
                    n_ev = ev_np.shape[0]
                    if n_ev > 0:
                        event_dtype = np.dtype([
                            ('x', np.int32),
                            ('y', np.int32),
                            ('t', np.int64),
                            ('p', np.int32),
                        ])
                        ev = np.zeros(n_ev, dtype=event_dtype)
                        ev['t'] = ev_np[:, 0]
                        ev['x'] = ev_np[:, 1]
                        ev['y'] = ev_np[:, 2]
                        ev['p'] = ev_np[:, 3]

                        # generate representation
                        rep = get_item_transform(
                            reshaped_return_data=ev,
                            representation_name=self.cfg["representation"],
                            height=self.height,
                            width=self.width,
                            num_events=n_ev,
                            cfg=self.cfg,
                            encoder=encoder,
                        )
                        rep = rep.reshape(-1, self.height, self.width)

                        # write representation frames
                        n_frames = rep.shape[0]
                        rep_ds.resize((idx_r + n_frames, self.height, self.width))
                        rep_ds[idx_r: idx_r + n_frames, :, :] = rep
                        idx_r += n_frames
                        rep_lengths.append(n_frames)
                    else:
                        # no events -> zero-length
                        rep_lengths.append(0)

                    # write bounding boxes
                    n_bb = bb_np.shape[0]
                    if n_bb > 0:
                        bboxes_ds.resize((idx_b + n_bb, 5))
                        bboxes_ds[idx_b: idx_b + n_bb, :] = bb_np
                        idx_b += n_bb
                    bbox_lengths.append(n_bb)

                # save new splits arrays
                rep_splits_out = np.concatenate(([0], np.cumsum(rep_lengths, dtype=np.int64)))
                bbox_splits_out = np.concatenate(([0], np.cumsum(bbox_lengths, dtype=np.int64)))
                out_h5.create_dataset("rep_splits", data=rep_splits_out)
                out_h5.create_dataset("bboxes_splits", data=bbox_splits_out)
                out_h5.flush()

    def setup(self, stage=None):
        base = Path(self.save_dir)
        if not base.exists():
            raise FileNotFoundError(f"Representation files not found at {base}")
        
        self.train_data = MosaicDetection(base / "train.h5",   
                                          img_size=self.img_size,
                                            mosaic=True,
                                            preproc=TrainTransform(
                                                max_labels=120,
                                                flip_prob=0.5,
                                                hsv_prob=0.0))
        
        self.val_data   = MosaicDetection(base / "val.h5",   
                                          img_size=self.img_size,
                                            mosaic=False,
                                            preproc=TrainTransform(
                                                max_labels=120,
                                                flip_prob=0.0,
                                                hsv_prob=0.0))
        
        self.test_data  = MosaicDetection(base / "test.h5",   
                                          img_size=self.img_size,
                                            mosaic=False,
                                            preproc=TrainTransform(
                                                max_labels=120,
                                                flip_prob=0.0,
                                                hsv_prob=0.0))

    def collate_fn(self, batch):
        reps, bbs = zip(*batch)
        # stack representations along batch dimension
        batch_reps = torch.stack(reps, dim=0)
        # concatenate all bboxes and create batch indices
        if len(bbs) > 0:
            bboxes = torch.cat(bbs, dim=0)
            batch_idx = torch.cat([
                torch.full((bb.size(0),), i, dtype=torch.long)
                for i, bb in enumerate(bbs)
            ], dim=0)
        else:
            bboxes = torch.empty((0, 5), dtype=torch.int32)
            batch_idx = torch.empty((0,), dtype=torch.long)

        return {
            "representations": batch_reps,
            "bboxes":           bboxes,
            "batch_idx":        batch_idx,
        }

    def train_dataloader(self):
        return DataLoader(
            self.train_data,
            batch_size=self.cfg["batch_size"],
            num_workers=self.cfg["num_workers"],
            pin_memory=True,
            shuffle=True,
            collate_fn=self.collate_fn,
            persistent_workers=False
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_data,
            batch_size=self.cfg["batch_size"],
            num_workers=self.cfg["num_workers"],
            pin_memory=True,
            shuffle=False,
            collate_fn=self.collate_fn,
            persistent_workers=True
        )

    def test_dataloader(self):
        return DataLoader(
            self.test_data,
            batch_size=self.cfg["batch_size"],
            num_workers=self.cfg["num_workers"],
            pin_memory=True,
            shuffle=False,
            collate_fn=self.collate_fn,
            persistent_workers=True
        )
