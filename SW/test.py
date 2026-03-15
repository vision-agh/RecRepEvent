import yaml
import lightning as L


from lightning.pytorch.loggers.wandb import WandbLogger
from lightning.pytorch.callbacks import ModelCheckpoint, LearningRateMonitor

from data.gen1.detection.gen1 import Gen1
from representations.ordering_event_representation import get_optimized_representation
import matplotlib.pyplot as plt
from representations.get_representation import get_item_transform

from models.detection.detection import LNDetection

import matplotlib.pyplot as plt
def main(args):
    # Load the configuration file
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)

    dm = Gen1(cfg=config)
    dm.setup()

    print(dm.val_data)


    for idx, batch in enumerate(dm.val_dataloader()):

        if idx > 2:
            dm.val_data.change_mosaic_prob(0.0)
        print(batch['representations'][0].shape)

        img = batch['representations'][0].numpy()
        bbox = batch['bboxes'].numpy()
        batch_idx = batch['batch_idx'].numpy()

        print(bbox.shape)
        img = img.transpose(1, 2, 0)
        imgx = img[..., :3]

        bbox = bbox[batch_idx == 0]
        # add bounding boxe
        import numpy as np

        for i in range(bbox.shape[0]):
            cx, cy, w, h = bbox[i, 1:5]
            if cx == cy == w == h == 0:
                continue

            print(w, h)
            x1 = int(cx - w / 2)
            y1 = int(cy - h / 2)
            x2 = int(cx + w / 2)
            y2 = int(cy + h / 2)
            
            x1 = np.clip(x1, 0, imgx.shape[1] - 1)
            y1 = np.clip(y1, 0, imgx.shape[0] - 1)
            x2 = np.clip(x2, 0, imgx.shape[1] - 1)
            y2 = np.clip(y2, 0, imgx.shape[0] - 1)
            imgx[int(y1):int(y2), int(x1), :] = 255
            imgx[int(y1):int(y2), int(x2), :] = 255
            imgx[int(y1), int(x1):int(x2), :] = 255
            imgx[int(y2), int(x1):int(x2), :] = 255

        plt.imshow(imgx.astype('uint8'), vmin=0, vmax=255)
        plt.show()
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train a model with a configuration file.")
    parser.add_argument('--config', 
                        type=str,
                        default='config/gen1.yaml',
                        help='Path to the configuration file.')
    args = parser.parse_args()
    main(args)