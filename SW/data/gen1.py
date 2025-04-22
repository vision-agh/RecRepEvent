import os
import glob
import gc
import multiprocessing as mp
import psutil
from pathlib import Path

import numpy as np
import h5py
import lightning as L
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from data.readers.extractor_gen1 import Gen1Reader
from data.utils.bbox_filters import apply_filters
from data.base import EventDataset


def log_mem(stage: str):
    mb = psutil.Process(os.getpid()).memory_info().rss / 1024**2
    print(f"[{stage}] RSS = {mb:.1f} MB")


def iter_samples(file_path: str, cfg: dict):
    """Yield (ev, bb) pairs one by one—no list ever built."""
    reader = Gen1Reader(file_path)
    ann_file = file_path.replace("_td.dat.h5", "_bbox.npy")
    mode = Path(file_path).parent.name

    anns = np.load(ann_file)
    anns = apply_filters(anns, mode, cfg, dataset_type="gen1")
    for t_bbox in np.unique(anns["t"]).astype(np.int64):
        t0, t1 = t_bbox - 100_000, t_bbox + 100_000
        ev = reader.extract_timewindow(t0, t1)
        ev = np.stack([ev["t"], ev["x"], ev["y"], ev["p"]], axis=1).astype(np.float32)
        if ev.shape[0] == 0:
            continue
        ev[:, 0] = (ev[:, 0] - t0) / (t1 - t0)

        bb = anns[anns["t"] == t_bbox]
        bb = np.array(bb.tolist())[:, 1:6].astype(np.int32)

        yield ev, bb

    reader.close()


def _worker_proc(file_list, queue, cfg):
    """
    Worker process: extract samples from each file in file_list
    and put them onto the queue.  At the end, send a None sentinel.
    """
    for fp in file_list:
        log_mem(f"After {fp}")
        for ev, bb in iter_samples(fp, cfg):
            queue.put((ev, bb))
    queue.put(None)  # signal “I’m done”


def _writer_proc(queue, out_path, num_workers):
    """
    Writer process: consumes items from the queue (ev, bb) tuples,
    appends them straight into HDF5.  Exits once it has seen N sentinels.
    """
    events_lengths = []
    bboxes_lengths = []

    with h5py.File(out_path, "w") as f:
        events_ds = f.create_dataset(
            "events", shape=(0, 4), maxshape=(None, 4),
            dtype="float32", chunks=(1024, 4)
        )
        bboxes_ds = f.create_dataset(
            "bboxes", shape=(0, 5), maxshape=(None, 5),
            dtype="int32",   chunks=(1024, 5)
        )

        idx_e = 0
        idx_b = 0
        done_workers = 0

        while done_workers < num_workers:
            item = queue.get()
            if item is None:
                done_workers += 1
                continue

            ev, bb = item
            # append events
            n_e = ev.shape[0]
            events_ds.resize(idx_e + n_e, axis=0)
            events_ds[idx_e: idx_e + n_e, :] = ev
            idx_e += n_e
            events_lengths.append(n_e)

            # append bboxes
            n_b = bb.shape[0]
            bboxes_ds.resize(idx_b + n_b, axis=0)
            bboxes_ds[idx_b: idx_b + n_b, :] = bb
            idx_b += n_b
            bboxes_lengths.append(n_b)
        
        events_splits  = np.concatenate(([0], np.cumsum(events_lengths, dtype=np.int64)))
        bboxes_splits  = np.concatenate(([0], np.cumsum(bboxes_lengths, dtype=np.int64)))

        f.create_dataset("events_splits",  data=events_splits)
        f.create_dataset("bboxes_splits",  data=bboxes_splits)

        f.flush()
    # once closed, exit automatically


class Gen1(L.LightningDataModule):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

    def prepare_data(self):
        os.makedirs(self.cfg["dir_to_save"], exist_ok=True)

        # enforce 'spawn' for true process isolation
        ctx = mp.get_context("spawn")

        for split in ["train", "val", "test"]:
            out_path = Path(self.cfg["dir_to_save"]) / f"{split}.h5"
            if out_path.exists():
                continue

            files = sorted(glob.glob(os.path.join(self.cfg["data_dir"], split, "*.h5")))
            log_mem(f"Before {split}")

            # 1) build a bounded queue
            queue = ctx.Queue(maxsize=500)

            # 2) start the writer
            writer = ctx.Process(
                target=_writer_proc,
                args=(queue, str(out_path), self.cfg["num_processes"]),
                daemon=True
            )
            writer.start()

            # 3) split work evenly
            n = self.cfg["num_processes"]
            chunks = [files[i::n] for i in range(n)]

            # 4) start N workers
            procs = []
            for chunk in chunks:
                p = ctx.Process(
                    target=_worker_proc,
                    args=(chunk, queue, self.cfg),
                    daemon=True
                )
                p.start()
                procs.append(p)

            # 5) wait for all extractors to finish
            for p in procs:
                p.join()

            # 6) wait for writer to finish consuming all sentinels
            writer.join()

    def setup(self, stage=None):
        base = Path(self.cfg["dir_to_save"])
        self.train_data = EventDataset(base / "train.h5", self.cfg)
        self.val_data   = EventDataset(base / "val.h5",   self.cfg)
        self.test_data  = EventDataset(base / "test.h5",  self.cfg)

    def collate_fn(self, batch):
        packed_events, masks, counts, bbs = zip(*batch)

        bboxes = []
        batch_idx = []

        for idx, bb in enumerate(bbs):
            num_bboxes = bb.size(0)
            bboxes.append(bb)
            batch_idx.append(torch.full((num_bboxes,), idx, dtype=torch.long))

        batch_bboxes = torch.cat(bboxes, dim=0)          # [sum_num_bboxes, 5]
        batch_indices = torch.cat(batch_idx, dim=0)     # [sum_num_bboxes]
        
        return {
            "packed_events":    packed_events,
            "mask":             masks,
            "counts_per_pixel": counts,
            "bboxes":           batch_bboxes,
            "batch_bbox":       batch_indices,
        }

    def _make_loader(self, ds, shuffle=False):
        return DataLoader(
            ds,
            batch_size=self.cfg["batch_size"],
            num_workers=self.cfg["num_workers"],
            shuffle=shuffle,
            collate_fn=self.collate_fn,
            persistent_workers=False,
        )

    def train_dataloader(self): return self._make_loader(self.train_data, shuffle=True)
    def val_dataloader(self):   return self._make_loader(self.val_data)
    def test_dataloader(self):  return self._make_loader(self.test_data)
