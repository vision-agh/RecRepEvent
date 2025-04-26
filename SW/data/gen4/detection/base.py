import h5py
import numpy as np
import torch
import torchvision.transforms as transforms


from torch.utils.data import Dataset
from utils.pack_events import pack_events_parallel


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

        rep = transforms.Resize((640, 640))(rep)

        bbox[:, 0] *= 640 / 1280  # x1
        bbox[:, 1] *= 640 / 720 # y1
        bbox[:, 2] *= 640 / 1280  # x2
        bbox[:, 3] *= 640 / 720 # y2
        return rep, bbox

