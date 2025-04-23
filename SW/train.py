import yaml
import numpy as np
import lightning as L
import torch
import argparse
import multiprocessing as mp

from data.gen1 import Gen1
from models.recurrent.autoencoder import AutoEncoder
from utils.pack_events import pack_events_parallel
from lightning.pytorch.loggers.wandb import WandbLogger
from lightning.pytorch.callbacks import ModelCheckpoint, LearningRateMonitor

def main(args):
    # Load the configuration file
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)

    dm = Gen1(cfg=config)
    dm.prepare_data()
    dm.setup()

    model = AutoEncoder(cfg=config)

    wandb_logger = WandbLogger(project=f"Recurrent_Event_Representation", 
                               name=f"first_run")
    wandb_logger.watch(model)

    lr_monitor = LearningRateMonitor(logging_interval='step')
    checkpoint_callback = ModelCheckpoint(
        dirpath='checkpoints',
        filename=f'my_gru_checkpoint',
        monitor='val_loss',
        mode='min',
        save_top_k=1
    )

    trainer = L.Trainer(max_epochs=100, 
                        logger=wandb_logger, 
                        callbacks=[lr_monitor, checkpoint_callback],
                        log_every_n_steps=1,
                        check_val_every_n_epoch=2,
                        deterministic=True,
                        limit_train_batches=1000,
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