FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu22.04

# System dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install PyTorch nightly
RUN pip install --upgrade pip setuptools wheel

RUN pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

RUN pip install lightning wandb

RUN pip install opencv-python matplotlib tqdm h5py hdf5plugin

WORKDIR /workspace
COPY . /workspace
