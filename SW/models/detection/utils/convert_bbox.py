import torch

def convert_to_training_format(bbox, batch, batch_size):
    max_detections = 100
    targets = torch.zeros(size=(batch_size, max_detections, 5), dtype=torch.float32, device=bbox.device)
    unique, counts = torch.unique(batch, return_counts=True)
    counter = _sequential_counter(counts)

    bbox = bbox.clone()
    # xywhlc pix -> lcxcywh pix
    bbox[:, :2] += bbox[:, 2:4] * .5
    # lcxcywh cls -> cls lcxcywh
    bbox = torch.roll(bbox[:, :5], dims=1, shifts=1)

    targets[batch, counter] = bbox

    return targets

def _sequential_counter(counts: torch.LongTensor):
    """
    Returns a torch tensor which counts up for each count
    Example: counts = [2,4,6,2,4] then the output will be
    output = [0,1,0,1,2,3,0,1,2,3,4,5,0,1,0,1,2,3]
    """
    assert counts.dtype == torch.long
    assert len(counts.shape) > 0
    assert (counts >= 0).all()

    len_counter = counts.sum()
    tensors_kwargs = dict(device=counts.device, dtype=torch.long)

    # first construct delta function, which has value c_N at position sum_k=0^N c_k
    delta = torch.zeros(size=(len_counter,), **tensors_kwargs)
    x_coord = counts.cumsum(dim=0)
    delta[x_coord[:-1]] = counts[:-1]

    # next construct step function, and the result it a linear function minus this step function
    step = delta.cumsum(dim=0)
    counter = torch.arange(len_counter, **tensors_kwargs) - step

    return counter