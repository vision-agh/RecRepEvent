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

    if args.representation:
        config["representation"] = args.representation

    print(config)

    dm = Gen1(cfg=config)
    dm.prepare_data()
    dm.setup()

    model = LNDetection(config, train_dataloader_len=len(dm.train_dataloader()))

    print(model)

    lr_monitor = LearningRateMonitor(logging_interval='step')
    wandb_logger = WandbLogger(project=f'Detection Recurrent', 
                                group=config["name"],
                                name=config["representation"])
    
    wandb_logger.watch(model)
    checkpoint_callback = ModelCheckpoint(
        dirpath='checkpoints',
        filename=f'Detection_{config["name"]}_{config["representation"]}',
        monitor='val/mAP',
        mode='max',
        save_top_k=1
    )

    trainer = L.Trainer(max_epochs=100, 
                        log_every_n_steps=1, 
                        logger=wandb_logger,
                        callbacks=[lr_monitor, checkpoint_callback],
                        deterministic=True,
                        check_val_every_n_epoch=2,
                        precision='16-mixed',
                        gradient_clip_val=1.0,
                        gradient_clip_algorithm='value',
                        devices=1)

    trainer.fit(model, dm)

    model = LNDetection.load_from_checkpoint(checkpoint_callback.best_model_path)
    trainer.test(model, datamodule=dm)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train a model with a configuration file.")
    parser.add_argument('--config', 
                        type=str,
                        default='config/gen1.yaml',
                        help='Path to the configuration file.')
    parser.add_argument('--representation',
                        type=str,
                        default=None,
                        help='Representation to use for training.')
    args = parser.parse_args()
    main(args)