import h5py
import numpy as np
import torch
from torch.utils.data import Dataset
from utils.pack_events import pack_events_parallel

import torchvision.transforms as transforms

class EventDatasetRepresentation(Dataset):
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

        self.augment = augment

        # Augmentation


    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        # lazily open
        if self._h5f is None:
            self._h5f   = h5py.File(self.filepath, "r")
            self._ds_ev = self._h5f["representation"]
            self._ds_bb = self._h5f["bboxes"]

        # figure out our slice in the flat arrays
        e_start = int(self.events_splits[idx])
        e_end   = int(self.events_splits[idx+1])
        b_start = int(self.bboxes_splits[idx])
        b_end   = int(self.bboxes_splits[idx+1])

        # pull out just our events & bboxes
        ev_np = self._ds_ev[e_start:e_end]      # shape = (n_ev, 4)
        bb_np = self._ds_bb[b_start:b_end]      # shape = (n_bb, 5)

        rep = torch.from_numpy(ev_np)
        bbox = torch.from_numpy(bb_np)


        return rep, bbox
