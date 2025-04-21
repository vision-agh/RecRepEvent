import numpy as np
import h5py

class Gen1Reader:
    def __init__(self, h5_file):
        self.h5f = h5py.File(str(h5_file), 'r')
        self.all_times = None

    def max_time(self):
        return self.h5f['events']['t'][-1]
    
    def close(self):
        self.h5f.close()

    @property
    def time(self) -> np.ndarray:
        if self.all_times is None:
            self.all_times = np.asarray(self.h5f['events']['t'])
            self._correct_time(self.all_times)
        return self.all_times
    
    @staticmethod
    def _correct_time(time_array: np.ndarray):
        assert time_array[0] >= 0
        time_last = 0
        for idx, time in enumerate(time_array):
            if time < time_last:
                time_array[idx] = time_last
            else:
                time_last = time

    def extract_timewindow(self, t_start: int, t_end: int):
        idx_start = np.searchsorted(self.time, t_start)
        idx_end = np.searchsorted(self.time, t_end)

        return self.get_event_slice(idx_start, idx_end)
    
    def get_event_slice(self, idx_start: int, idx_end: int):
        ev_data = self.h5f['events']
        x_new = np.asarray(ev_data['x'][idx_start:idx_end], dtype='int64')
        y_new = np.asarray(ev_data['y'][idx_start:idx_end], dtype='int64')
        p_new = np.asarray(ev_data['p'][idx_start:idx_end], dtype='int64')
        #p_new = np.clip(p_new, a_min=0, a_max=None)
        t_new = np.asarray(self.time[idx_start:idx_end], dtype='int64')

        output = {'p': p_new, 't': t_new, 'x': x_new, 'y': y_new,}
        return output