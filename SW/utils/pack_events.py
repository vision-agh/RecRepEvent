import torch


def pack_events_parallel(events, H, W, include_polarity=False):
    """
    events: (N,4) tensor of [time, x, y, polarity]
    H, W: ints, image height & width
    include_polarity: if True, output D=2 (time+polarity); else D=1 (time only)

    returns:
      out: (L, H*W, D) tensor, where L = max events per pixel
      counts_per_pixel: (H*W,) count of events at each pixel
    """
    # 1) unpack
    t = events[:, 0]
    x = events[:, 1].long()
    y = events[:, 2].long()
    p = events[:, 3]

    # 2) flatten pixel indices
    pixel_id = y * W + x                    # shape (N,)

    # 3) sort by time then by pixel (stable) → sorted_idx
    time_order = torch.argsort(t)           
    pixel_then_time = torch.argsort(pixel_id[time_order], stable=True)
    sorted_idx = time_order[pixel_then_time]

    # apply the sort
    pix_sorted  = pixel_id[sorted_idx]      # (N,)
    D = 2 if include_polarity else 1
    feat_all    = events[:, [0,3]] if include_polarity else events[:, [0]]
    feat_sorted = feat_all[sorted_idx]      # (N, D)

    # 4) counts and max length
    counts_per_pixel = torch.bincount(pixel_id, minlength=H*W)  # (H*W,)
    L = counts_per_pixel.max().item()

    # 5) build an “offset” array so that for each pixel k,
    #    events belonging to k occupy positions
    #      [offsets[k], offsets[k+1]) in the sorted list.
    offsets = torch.empty((H*W+1,), dtype=torch.long, device=events.device)
    offsets[0] = 0
    offsets[1:] = counts_per_pixel.cumsum(dim=0)

    # 6) for each sorted event j, its slot = j - offsets[pix_sorted[j]]
    positions = torch.arange(pix_sorted.size(0), device=events.device)
    ranks = positions - offsets[pix_sorted]   # (N,)

    # 7) scatter all at once into the output tensor
    out = torch.zeros(L, H*W, D, device=events.device)
    out[ranks, pix_sorted] = feat_sorted

    # 8) generate mask for valid events
    mask = torch.zeros(L, H*W, dtype=torch.bool, device=events.device)
    mask[ranks, pix_sorted] = True

    return out, counts_per_pixel, mask
