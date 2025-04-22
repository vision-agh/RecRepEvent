import yaml
import numpy as np
import lightning as L
import torch
import argparse
import multiprocessing as mp
import matplotlib.pyplot as plt

from data.gen1 import Gen1
from models.encoder import Encoder
from utils.pack_events import pack_events_parallel
from utils.unpack_embeddings import unpack_embeddings
from lightning.pytorch.loggers.wandb import WandbLogger

def main(args):
    # Load the configuration file
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)

    config["remove_empty_pixels"] = False
    config["crop_events_spatially"] = False

    dm = Gen1(cfg=config)
    dm.setup()

    model = Encoder(input_size=2, hidden_size=12, num_bits=8).eval().cuda()
    model.compile()

    checkpoint = torch.load("checkpoints/my_gru_checkpoint-v7.ckpt")
    encoder_weights = {k.replace("encoder.", ""): v for k, v in checkpoint["state_dict"].items() if k.startswith("encoder.")}
    model.load_state_dict(encoder_weights, strict=False)

    # Plot 12 channels in 3x4 grid without closing the figure (updating it)

    fig, axes = plt.subplots(3, 4, figsize=(12, 9))
    imgs = []

    # Inicjalizujemy puste obrazy
    for ax in axes.flatten():
        img = ax.imshow(np.zeros((config["sensor_size"]["H"], config["sensor_size"]["W"])), cmap='hot', vmin=0, vmax=255)
        ax.axis('off')
        imgs.append(img)

    plt.tight_layout()
    # bar
    plt.colorbar(imgs[0], ax=axes, orientation='vertical', fraction=0.02, pad=0.04)
    plt.ion()  # Tryb interaktywny
    plt.show()
        
    for i, batch in enumerate(dm.val_dataloader()):
        events = batch['packed_events'].squeeze(0)
        counts_per_pixel = batch['counts_per_pixel'].squeeze(0)
        bboxes = batch['bboxes'].squeeze(0)

        embeddings = model(events.cuda())

        u_embeddings = unpack_embeddings(embeddings, 
                                        config["sensor_size"]["H"], 
                                        config["sensor_size"]["W"],
                                        counts_per_pixel)
        
        u_embeddings = u_embeddings.detach().cpu().numpy()

        # Change from (3, H, W) to (H, W, 3)
        img = np.transpose(u_embeddings, (1, 2, 0))
        img = img / np.max(img)
        img = img * 255
        img = img.astype(np.uint8)

        for j in range(12):
            one_channel = img[:, :, j]
            # show bounding boxes
            for b in bboxes:
                x, y, w, h = b[0], b[1], b[2], b[3]
                one_channel[y:y+h, x] = 255
                one_channel[y:y+h, x+w] = 255
                one_channel[y, x:x+w] = 255
                one_channel[y+h, x:x+w] = 255

            imgs[j].set_data(one_channel)
            imgs[j].set_clim(vmin=0, vmax=255)  # opcjonalnie – jeśli wartości się zmieniają dynamicznie

        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(.1)



if __name__ == "__main__":
    L.seed_everything(42)
    mp.set_start_method('fork', force=True)

    parser = argparse.ArgumentParser(description="Train a model with a configuration file.")
    parser.add_argument('--config', 
                        type=str,
                        default='config/general.yaml',
                        help='Path to the configuration file.')

    args = parser.parse_args()
    main(args)