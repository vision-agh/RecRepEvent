import yaml
import lightning as L


from lightning.pytorch.loggers.wandb import WandbLogger
from lightning.pytorch.callbacks import ModelCheckpoint, LearningRateMonitor

from data.gen1.detection.gen1 import Gen1
from representations.ordering_event_representation import get_optimized_representation
import matplotlib.pyplot as plt
from representations.get_representation import get_item_transform

from models.detection.detection import LNDetection

def main(args):
    # Load the configuration file
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)

    config["representation"] = args.representation
    dm = Gen1(cfg=config)
    dm.prepare_data()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train a model with a configuration file.")
    parser.add_argument('--config', 
                        type=str,
                        default='config/gen1.yaml',
                        help='Path to the configuration file.')
    parser.add_argument('--representation',
                        type=str,
                        default='ToVoxelGrid',
                        help='Type of the representation.')
    args = parser.parse_args()
    main(args)