import torch

def pack_events_parallel(events, H, W, include_polarity=False, max_events_per_pixel=100):
    """
    events: (N,4) tensor of [time, x, y, polarity]
    H, W: ints, image height & width
    include_polarity: if True, output D=2 (time+polarity); else D=1 (time only)
    max_events_per_pixel: int or None, maximum number of events to keep per pixel (hot pixel removal)
    
    returns:
      out: (L, H*W, D) tensor, where L = min(max_events_per_pixel, max events per pixel) if specified, otherwise L = max events per pixel
      counts_per_pixel: (H*W,) count of events per pixel (clamped if max_events_per_pixel is set)
      mask: (L, H*W) boolean tensor, True for valid events in out
    """
    # 1) unpack
    t = events[:, 0]
    x = events[:, 1].long()
    y = events[:, 2].long()
    p = events[:, 3]

    # 2) flatten pixel indices
    pixel_id = y * W + x                    # shape (N,)

    # 3) sort by time then by pixel (stable)
    time_order = torch.argsort(t)
    pixel_then_time = torch.argsort(pixel_id[time_order], stable=True)
    sorted_idx = time_order[pixel_then_time]

    pix_sorted  = pixel_id[sorted_idx]
    D = 2 if include_polarity else 1
    feat_all    = events[:, [0, 3]] if include_polarity else events[:, [0]]
    feat_sorted = feat_all[sorted_idx]

    # 4) compute original counts per pixel
    counts_all = torch.bincount(pixel_id, minlength=H*W)

    # 5) determine L and clamp counts if needed
    if max_events_per_pixel is not None:
        counts_per_pixel = torch.minimum(counts_all, torch.tensor(max_events_per_pixel, device=events.device))
        L = int(counts_per_pixel.max().item())
    else:
        counts_per_pixel = counts_all
        L = int(counts_all.max().item())

    # 6) compute original offsets for ranking
    offsets = torch.empty((H*W+1,), dtype=torch.long, device=events.device)
    offsets[0] = 0
    offsets[1:] = counts_all.cumsum(dim=0)

    # 7) compute ranks of each event within its pixel
    positions = torch.arange(pix_sorted.size(0), device=events.device)
    ranks_all = positions - offsets[pix_sorted]

    # 8) optionally filter out hot pixel events beyond the max
    if max_events_per_pixel is not None:
        keep = ranks_all < max_events_per_pixel
        pix_sorted = pix_sorted[keep]
        feat_sorted = feat_sorted[keep]
        ranks = ranks_all[keep]
    else:
        ranks = ranks_all

    # 9) scatter into output tensor
    out = torch.zeros(L, H*W, D, device=events.device)
    out[ranks, pix_sorted] = feat_sorted

    # 10) generate mask for valid events
    mask = torch.zeros(L, H*W, dtype=torch.bool, device=events.device)
    mask[ranks, pix_sorted] = True

    return out, counts_per_pixel, mask
