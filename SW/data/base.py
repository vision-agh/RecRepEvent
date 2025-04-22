import h5py
import numpy as np
import torch
from torch.utils.data import Dataset
from utils.pack_events import pack_events_parallel

class EventDataset(Dataset):
    def __init__(self, filepath: str, cfg):
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
            self.events_splits = f["events_splits"][:]      # e.g. [0, 100, 250, ...]
            self.bboxes_splits = f["bboxes_splits"][:]
        self.num_samples = len(self.events_splits) - 1

        # Will open the file & datasets once per worker
        self._h5f    = None
        self._ds_ev  = None
        self._ds_bb  = None

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        # lazily open
        if self._h5f is None:
            self._h5f   = h5py.File(self.filepath, "r")
            self._ds_ev = self._h5f["events"]
            self._ds_bb = self._h5f["bboxes"]

        # figure out our slice in the flat arrays
        e_start = int(self.events_splits[idx])
        e_end   = int(self.events_splits[idx+1])
        b_start = int(self.bboxes_splits[idx])
        b_end   = int(self.bboxes_splits[idx+1])

        # pull out just our events & bboxes
        ev_np = self._ds_ev[e_start:e_end]      # shape = (n_ev, 4)
        bb_np = self._ds_bb[b_start:b_end]      # shape = (n_bb, 5)

        bboxes = torch.from_numpy(bb_np).long()

        ev_np = ev_np[:50000]  # take only the first 5000 events
        # to torch
        ev = torch.from_numpy(ev_np).float()

        # optional spatial cropping as before
        if self.cfg.get("crop_events_spatially", False):
            cs = self.cfg["crop_window"]
            H, W = self.cfg["sensor_size"]["H"], self.cfg["sensor_size"]["W"]
            x1 = np.random.randint(0, W - cs + 1)
            y1 = np.random.randint(0, H - cs + 1)
            m = (
                (ev[:,1] >= x1) & (ev[:,1] < x1+cs) &
                (ev[:,2] >= y1) & (ev[:,2] < y1+cs)
            )
            ev = ev[m]
            if len(ev) < 2 or (ev[:,1].max() - ev[:,1].min() == 0 and ev[:,2].max() - ev[:,2].min() == 0):
                ev = torch.from_numpy(ev_np[:5000]).float()

        # pack events into whatever tensor your model expects
        packed, counts, mask = pack_events_parallel(
            events=ev,
            H=self.cfg["sensor_size"]["H"],
            W=self.cfg["sensor_size"]["W"],
            include_polarity=True
        )

        # drop empty columns
        keep = counts > 0
        packed = packed[:, keep]
        mask   = mask[:, keep]

        return packed, mask, counts, bboxes
