import torch

def unpack_embeddings(embeddings, H, W, counts_per_pixel=None):
    """
    Unpack the embeddings into a tensor of shape (C, H, W) where C is the number of channels,
    H is the height, W is the width.
    
    Args:
        embeddings: (H*W, C) tensor of packed embeddings
        H: int, height of the image
        W: int, width of the image

    Returns:
        unpacked: (C, H, W)
    """
    # Unpack the embeddings
    if counts_per_pixel is not None:
        new_embeddings = torch.zeros((counts_per_pixel.size(0), embeddings.size(1)), device=embeddings.device)

        # non zero values in counts per pixel are the indices of the embeddings
        non_zero_indices = counts_per_pixel.nonzero(as_tuple=True)[0]
        # fill the unpacked tensor with the embeddings
        new_embeddings[non_zero_indices] = embeddings

        unpacked = new_embeddings.view(H, W, -1).permute(2, 0, 1)
    else:
        unpacked = embeddings.view(H, W, -1).permute(2, 0, 1)
        
    return unpacked