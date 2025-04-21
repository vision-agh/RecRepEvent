import os
import glob
import torch
import torch.nn as nn
import numpy as np
import lightning as L
import h5py
from pathlib import Path

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from concurrent.futures import ProcessPoolExecutor, as_completed
from torch.utils.data import DataLoader


from data.utils.write_to_h5 import H5Writer
from data.readers.extractor_gen1 import Gen1Reader
from data.utils.bbox_filters import apply_filters
from data.base import EventDataset


class Gen1(L.LightningDataModule):
    def __init__(self,
                 cfg):
        
        super().__init__()

        self.cfg = cfg

    def process_file_to_train(self, file_path: str):
        """
        Read one raw .h5 + its .npy annotation,
        extract all (events, bboxes) for that file,
        and return them as a list of tuples.
        """
        reader = Gen1Reader(file_path)
        ann_file = file_path.replace("_td.dat.h5", "_bbox.npy")
        dataset_mode = Path(file_path).parent.name

        anns = np.load(ann_file)
        anns = apply_filters(anns, dataset_mode, self.cfg, dataset_type="gen1")
        unique_ts = np.unique(anns["t"]).astype(np.int64)

        samples = []
        for t_bbox in unique_ts:
            t_start = t_bbox - 100000
            t_end   = t_bbox + 100000

            ev = reader.extract_timewindow(t_start, t_end)
            ev = np.stack([ev["t"], ev["x"], ev["y"], ev["p"]], axis=1).astype(np.float32)
            if ev.shape[0] == 0:
                continue

            bb = anns[anns["t"] == t_bbox]
            bb = np.array(bb.tolist())[:, 1:6].astype(np.int32)

            samples.append((ev, bb))

        reader.close()
        return samples

    def prepare_data(self):
        """Parallel‐process each file, stream results into one HDF5 file."""
        
        dataset_mode = 'val'

        os.makedirs(self.cfg["dir_to_save"], exist_ok=True)

        data_files = glob.glob(os.path.join(self.cfg["data_dir"], dataset_mode, "*.h5"))
        out_path = Path(self.cfg["dir_to_save"]) / f"{dataset_mode}.h5"


        if out_path.exists():
            # already created on a previous call
            return

        with h5py.File(out_path, "w") as f, \
             ProcessPoolExecutor(max_workers=self.cfg["num_processes"]) as executor:

            # Create the two variable‑length datasets up front
            ew = H5Writer(f, "events", (None, 4),  np.float32)
            bw = H5Writer(f, "bboxes", (None, 5), np.int32)

            # Submit all files for parallel processing
            futures = {
                executor.submit(self.process_file_to_train, fp): fp
                for fp in data_files
            }

            # As soon as a file is done, write its samples into HDF5
            for future in tqdm(as_completed(futures),
                               total=len(futures),
                               desc="Processing & writing"):
                samples = future.result()
                for ev, bb in samples:
                    ew.add_data(ev)
                    bw.add_data(bb)


        
    def generate_ds(self, mode):
        file = Path(self.cfg["dir_to_save"]) / f"{mode}.h5"
        return EventDataset(file, self.cfg)
            
    def setup(self, stage=None):
        # Load training and testing data.
        self.train_data = self.generate_ds('val')
        # self.test_data = self.generate_ds('test')
        self.val_data = self.generate_ds('val')

    def collate_fn(self, batch):
        # Unzip the batch into events and bboxes
        batch_packed_events, batch_mask = zip(*batch)

        return {
            "packed_events": torch.stack(batch_packed_events),
            "mask": torch.stack(batch_mask)}


    def train_dataloader(self):
        return DataLoader(self.train_data, 
                          batch_size=self.cfg['batch_size'], 
                          num_workers=self.cfg['num_workers'], 
                          shuffle=True, 
                          collate_fn=self.collate_fn, 
                          persistent_workers=False)

    def val_dataloader(self):
        return DataLoader(self.val_data, 
                          batch_size=self.cfg['batch_size'], 
                          num_workers=self.cfg['num_workers'], 
                          shuffle=False, 
                          collate_fn=self.collate_fn, 
                          persistent_workers=False)
    
    def test_dataloader(self):
        return DataLoader(self.test_data, 
                          batch_size=self.cfg['batch_size'], 
                          num_workers=self.cfg['num_workers'], 
                          shuffle=False, 
                          collate_fn=self.collate_fn, 
                          persistent_workers=False)
    