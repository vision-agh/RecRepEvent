import torch
import glob
import h5py
import numpy as np


from torch.utils.data import Dataset
from utils.pack_events import pack_events_parallel

class EventDataset(Dataset):
    def __init__(self, filepath: str, cfg, min_events: int = 0, max_events: int = None):
        """
        filepath: path to the .h5 file
        cfg:      your config dict
        min_events, max_events: optionally gate samples by number of events
        """
        self.filepath = filepath
        self.cfg = cfg

        # Open once, read only the small lengths & shape metadata, then close
        with h5py.File(self.filepath, "r") as f:
            lengths = f["events_lengths"][:]  
            self.trail_ev = tuple(f.attrs["events_trailing_shape"])
            self.lengths_ev = lengths

            lengths_bb = f["bboxes_lengths"][:]
            self.trail_bb = tuple(f.attrs["bboxes_trailing_shape"])
            self.lengths_bb = lengths_bb

        # Build a list of valid indices after gating on event count
        if max_events is None:
            max_events = np.inf
        valid = np.where((lengths >= min_events) & (lengths <= max_events))[0]
        self.indices = valid.tolist()

        # We'll lazily open the file *inside* each worker on first __getitem__ call
        self._h5f = None
        self._ds_ev = None
        self._ds_bb = None

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        real_i = self.indices[idx]

        # lazily open the file & datasets once per worker
        if self._h5f is None:
            self._h5f  = h5py.File(self.filepath, "r")
            self._ds_ev = self._h5f["events"]
            self._ds_bb = self._h5f["bboxes"]

        # read just this one sample (no bulk [:] calls!)
        flat_ev = self._ds_ev[real_i]
        events_all  = flat_ev.reshape(self.lengths_ev[real_i], *self.trail_ev)

        flat_bb = self._ds_bb[real_i]
        bboxes  = flat_bb.reshape(self.lengths_bb[real_i], *self.trail_bb)

        events_all = torch.from_numpy(events_all).float()

        # Normalize time to [0, 1]
        events_all[:, 0] = (events_all[:, 0] - events_all[:, 0].min()) / (events_all[:, 0].max() - events_all[:, 0].min())

        # cut window from events of shape (64, 64) randomly
        # assert there is at least one event in the window

        cs = 32
        x1 = np.random.randint(0, self.cfg["sensor_size"]["W"] - cs + 1)
        y1 = np.random.randint(0, self.cfg["sensor_size"]["H"] - cs + 1)
        x2, y2 = x1 + cs, y1 + cs

        m_x = (events_all[:,1] >= x1) & (events_all[:,1] < x2)
        m_y = (events_all[:,2] >= y1) & (events_all[:,2] < y2)
        mask_crop = m_x & m_y

        events_crop = events_all[mask_crop]
        if events_crop.shape[0] == 0:
            # fallback to first 1000 events if crop was empty
            events_crop = events_all[:1000]

        # pack events
        packed_events, counts_per_pixel, mask = pack_events_parallel(events=events_crop,
                                                                    H=self.cfg["sensor_size"]["H"],
                                                                    W=self.cfg["sensor_size"]["W"],
                                                                    include_polarity=True)

        packed_events = packed_events[:, counts_per_pixel > 0]
        mask = mask[:, counts_per_pixel > 0]
        return packed_events, mask
