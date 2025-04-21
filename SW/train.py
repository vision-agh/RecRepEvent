import yaml
import numpy as np
import lightning as L
import torch
import argparse
import multiprocessing as mp

from data.gen1 import Gen1
from models.autoencoder import AutoEncoder
from utils.pack_events import pack_events_parallel
from lightning.pytorch.loggers.wandb import WandbLogger

def main(args):
    # Load the configuration file
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)

    dm = Gen1(cfg=config)
    dm.setup()

    model = AutoEncoder(cfg=config)

    wandb_logger = WandbLogger(project=f"Recurrent_Event_Representation", 
                               name=f"first_run")
    wandb_logger.watch(model)

    trainer = L.Trainer(max_epochs=100, 
                        logger=wandb_logger, 
                        log_every_n_steps=1,
                        limit_train_batches=100,
                        limit_val_batches=100)
    
    trainer.fit(model, dm)


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