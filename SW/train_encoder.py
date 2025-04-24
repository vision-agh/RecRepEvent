import numpy as np
import lightning as L
import torch
import argparse
import omegaconf
import multiprocessing as mp
import wandb

from data.gen1_2_encoder import Gen1
from models.recurrent.autoencoder import AutoEncoder
from lightning.pytorch.loggers.wandb import WandbLogger
from lightning.pytorch.callbacks import ModelCheckpoint, LearningRateMonitor

def main(args):
    L.seed_everything(42)

    # Load the configuration file
    cfg = omegaconf.OmegaConf.load(args.config)

    dm = Gen1(cfg=cfg)
    dm.prepare_data()
    dm.setup()

    model = AutoEncoder(cfg=cfg)

    wandb_logger = WandbLogger(project=f"Recurrent_Event_Representation", 
                               name=f"encoder_{cfg.encoder.rnn_type}_float32")
    wandb_logger.watch(model)
    lr_monitor = LearningRateMonitor(logging_interval='step')

    print("\n#####################################################################################")
    print("############################### TRAINING FLOAT MODEL ################################")
    print("#####################################################################################\n")

    checkpoint_callback = ModelCheckpoint(
        dirpath='checkpoints',
        filename=f'best_model_{cfg.encoder.rnn_type}_float32',
        monitor='val_loss',
        mode='min',
        save_top_k=1
    )

    trainer = L.Trainer(max_epochs=100, 
                        logger=wandb_logger, 
                        callbacks=[lr_monitor, checkpoint_callback],
                        log_every_n_steps=1,
                        check_val_every_n_epoch=2,
                        # gradient_clip_val=0.5,
                        limit_train_batches=1000,
                        limit_val_batches=1000)
    
    trainer.fit(model, dm)
    best_model_path = checkpoint_callback.best_model_path
    print(f"\nBest float model saved at: {best_model_path}\n")
    pretrained_model = AutoEncoder.load_from_checkpoint(best_model_path, cfg=cfg)

    wandb.finish()
    
    print("\n#####################################################################################")
    print("############################### TRAINING QAT MODEL ################################")
    print("#####################################################################################\n")

    wandb_logger = WandbLogger(project=f"Recurrent_Event_Representation", 
                               name=f"encoder_{cfg.encoder.rnn_type}_qat")
    wandb_logger.watch(pretrained_model)
    pretrained_model.lr *= 0.5

    checkpoint_callback = ModelCheckpoint(
        dirpath='checkpoints',
        filename=f'best_model_{cfg.encoder.rnn_type}_calibrated',
        monitor='val_loss',
        mode='min',
        save_top_k=1
    )

    trainer = L.Trainer(max_epochs=10, 
                        logger=wandb_logger, 
                        callbacks=[lr_monitor, checkpoint_callback],
                        log_every_n_steps=1,
                        check_val_every_n_epoch=2,
                        # gradient_clip_val=0.5,
                        limit_train_batches=1000,
                        limit_val_batches=1000)

    pretrained_model.calibrate = True
    trainer.fit(pretrained_model, dm)
    best_model_path = checkpoint_callback.best_model_path
    print(f"\nBest model saved at: {best_model_path}\n")

if __name__ == "__main__":
    mp.set_start_method('fork', force=True)

    parser = argparse.ArgumentParser(description="Train a model with a configuration file.")
    parser.add_argument('--config', 
                        type=str,
                        default='config/gen1.yaml',
                        help='Path to the configuration file.')

    args = parser.parse_args()
    main(args)