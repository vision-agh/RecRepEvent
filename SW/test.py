import h5py
import weakref
from pathlib import Path
from typing import Tuple, Optional
import numpy as np

def _blosc_opts(**kwargs):
    # your existing blosc options helper
    return {}

class H5Writer:
    def __init__(self, h5f: h5py.File, key: str, data_shape: Tuple[Optional[int], ...], numpy_dtype: np.dtype):
        """
        If data_shape[0] is None, we treat this as a variable‑length dataset
        whose trailing dims are fixed by data_shape[1:].
        Otherwise we create a regular resizable dataset of shape (None, *data_shape).
        """
        assert len(data_shape) >= 1
        self.h5f = h5f
        self.key = key
        self.dtype = numpy_dtype
        self.data_shape = data_shape
        self.t_idx = 0

        if data_shape[0] is None:
            # variable-length along axis 0
            vlen_dt = h5py.vlen_dtype(self.dtype)
            self.ds = self.h5f.create_dataset(
                key,
                shape=(0,),
                maxshape=(None,),
                dtype=vlen_dt,
                **_blosc_opts(complevel=1, shuffle="byte"),
            )
            # companion dataset for the leading dimension lengths
            self.shape_ds = self.h5f.create_dataset(
                f"{key}_lengths",
                shape=(0,),
                maxshape=(None,),
                dtype="int64",
            )
            # store the trailing shape so we can reconstruct later
            self.h5f.attrs[f"{key}_trailing_shape"] = data_shape[1:]
        else:
            # fixed-shape case (resizable on axis 0)
            maxshape = (None,) + data_shape
            chunkshape = (1,) + data_shape
            self.ds = self.h5f.create_dataset(
                key,
                dtype=self.dtype.name,
                shape=chunkshape,
                chunks=chunkshape,
                maxshape=maxshape,
                **_blosc_opts(complevel=1, shuffle="byte"),
            )

    def add_data(self, data: np.ndarray):
        """Append one record, flattening if variable‑length."""
        assert data.dtype == self.dtype, f"{data.dtype=} != {self.dtype}"
        if self.data_shape[0] is None:
            # check trailing dims match
            trailing = self.data_shape[1:]
            assert data.ndim == 1 + len(trailing)
            assert data.shape[1:] == trailing

            new_size = self.t_idx + 1
            self.ds.resize((new_size,))
            self.shape_ds.resize((new_size,))

            flat = data.reshape(-1)
            self.ds[self.t_idx] = flat
            self.shape_ds[self.t_idx] = data.shape[0]
            self.t_idx = new_size
        else:
            # fixed-shape
            assert data.shape == self.data_shape
            new_size = self.t_idx + 1
            self.ds.resize(new_size, axis=0)
            self.ds[self.t_idx:new_size] = data
            self.t_idx = new_size


if __name__ == "__main__":

    # --- generate some dummy data ---
    events = [
        np.random.rand(np.random.randint(10, 50), 4).astype(np.float32)
        for _ in range(100)
    ]
    bboxes = [
        np.random.rand(np.random.randint(1, 10), 5).astype(np.float32)
        for _ in range(100)
    ]

    # --- write both into one file ---
    out_path = Path("varlen_data.h5")
    with h5py.File(out_path, "w") as f:
        ew = H5Writer(f, "events", (None, 4), np.float32)
        bw = H5Writer(f, "bboxes", (None, 5), np.float32)

        for ev, bb in zip(events, bboxes):
            ew.add_data(ev)
            bw.add_data(bb)

    # --- read back and reconstruct lists of arrays ---
    with h5py.File(out_path, "r") as f:
        # events
        trail_ev = tuple(f.attrs["events_trailing_shape"])
        lengths_ev = f["events_lengths"][:]
        flat_ev = f["events"][:]
        loaded_events = [
            flat_ev[i].reshape(lengths_ev[i], *trail_ev)
            for i in range(len(flat_ev))
        ]

        # bboxes
        trail_bb = tuple(f.attrs["bboxes_trailing_shape"])
        lengths_bb = f["bboxes_lengths"][:]
        flat_bb = f["bboxes"][:]
        loaded_bboxes = [
            flat_bb[i].reshape(lengths_bb[i], *trail_bb)
            for i in range(len(flat_bb))
        ]

    # sanity check
    assert all(
        np.allclose(loaded_events[i], events[i]) for i in range(len(events))
    )
    assert all(
        np.allclose(loaded_bboxes[i], bboxes[i]) for i in range(len(bboxes))
    )
    print("✅ Successfully wrote and read back events & bboxes in one file.")
