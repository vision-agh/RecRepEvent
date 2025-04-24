import torch
import numpy as np
import h5py
import yaml
from data.gen1_2_representation import Gen1
from representations.ordering_event_representation import get_optimized_representation
import matplotlib.pyplot as plt
from representations.get_representation import get_item_transform


def main(args):
    # Load the configuration file
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)
    config["batch_size"] = 1

    dm = Gen1(cfg=config)
    dm.prepare_data()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train a model with a configuration file.")
    parser.add_argument('--config', 
                        type=str,
                        default='config/general.yaml',
                        help='Path to the configuration file.')
    args = parser.parse_args()
    main(args)