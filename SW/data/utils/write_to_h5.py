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