# RecRepEvent

A hardware-software co-design system for event-based object detection using Dynamic Vision Sensors (DVS). The software trains a recurrent encoder to compress raw event streams into compact spatial representations, which are fed into a YOLOX-based object detector. The hardware implements the encoder on a Xilinx FPGA for edge deployment.

---

## Project Structure

```
RecRepEvent/
├── SW/                          # Software component
│   ├── config/                  # YAML configuration files (general, gen1, gen4)
│   ├── data/                    # Dataset loaders and preprocessing
│   ├── models/                  # Encoder, decoder, detection models
│   ├── representations/         # Event representation implementations
│   ├── utils/                   # Packing, quantization, scheduling utilities
│   ├── YOLOX/                   # Integrated YOLOX detection framework
│   ├── checkpoints/             # Saved model weights
│   ├── train_encoder.py         # Autoencoder training (float32 + QAT)
│   ├── train.py                 # Object detection training
│   ├── test.py                  # Evaluation script
│   ├── preprocess_rep.py        # Offline representation preprocessing
│   ├── visualisation.py         # Encoder embedding visualization
│   └── Dockerfile               # CUDA 12.8 + cuDNN container
│
└── HW/                          # Hardware component
    ├── EventRecRep.xpr           # Xilinx Vivado project
    └── EventRecRep.srcs/         # HDL source files and IP cores
```

---

## Architecture

### Encoder (Recurrent Autoencoder)

Raw DVS events `(t, x, y, p)` are packed per-pixel and processed by a 3-layer stacked `MyGRUCell`:

```
Raw Events (t, x, y, p)
  → pack_events_parallel()        # Sort by (pixel, time); shape: (L, K, 2)
  → MyGRU Encoder (3 layers, hidden=12)
  → unpack_embeddings()           # Sparse → dense; shape: (12, H, W)
```

The 12-channel embedding is the input to the detection backbone.

**GRU Cell Equations:**

$$r_t = \sigma(W_{ir} x_t + b_{ir} + W_{hr} h_{t-1} + b_{hr})$$
$$z_t = \sigma(W_{iz} x_t + b_{iz} + W_{hz} h_{t-1} + b_{hz})$$
$$n_t = \tanh(W_{in} x_t + b_{in} + r_t \odot (W_{hn} h_{t-1} + b_{hn}))$$
$$h_t = (1 - z_t) \odot n_t + z_t \odot h_{t-1}$$

Where $x_t$ is the input (normalized timestamp, polarity), $h_t$ is the hidden state, $r_t$ is the reset gate, and $z_t$ is the update gate.

### Detection

A ResNet18/34/50 backbone (modified for 12-channel input) feeds into a YOLOX detection head trained to detect `car` and `pedestrian` classes on the Gen1 dataset.

### Quantization-Aware Training (QAT)

After float32 pretraining, the encoder is fine-tuned with 8-bit QAT for integer-only FPGA inference. `Observer` modules track activation statistics; LUTs replace sigmoid/tanh for hardware-friendly computation.

---

## Event Representations

The `representations/` module supports multiple event-to-frame conversion strategies:

| Name | Channels | Description |
|------|----------|-------------|
| `Encoder` | 12 | Recurrent GRU embedding (trained) |
| `ToImage` | 2 | Polarity-separated accumulation |
| `ToVoxelGrid` | 12 | Temporal binning |
| `MixedDensityEventStack` | 12 | Multi-window aggregation (max, sum, mean, var) |
| `ToTimesurface` | 2 | Exponential decay time surface |
| `TORE` | — | Temporal Ordering Representation |

---

## Setup

### Option 1: Docker

```bash
cd SW
docker build -t rec-rep .
docker run -it --rm --gpus all -v $(pwd):/workspace -w /workspace rec-rep
```

### Option 2: Conda

```bash
conda create -n dvs_rec python=3.10
conda activate dvs_rec

# PyTorch nightly with CUDA 12.8
pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# HDF5 support
conda install h5py
conda install blosc-hdf5-plugin -c conda-forge

# Other dependencies
pip install omegaconf opencv-python matplotlib psutil wandb lightning tonic numba pycocotools

# YOLOX
git clone https://github.com/Megvii-BaseDetection/YOLOX
cd YOLOX && pip install -v -e .
```

---

## Training

### 1. Train the Encoder

Trains a recurrent autoencoder on raw event streams, then fine-tunes with QAT:

```bash
python train_encoder.py --config config/gen1.yaml
```

Training proceeds in two stages:
- **Stage 1**: Float32 training for 100 epochs (MSE loss on reconstructed timestamps and polarity)
- **Stage 2**: QAT fine-tuning for 10 epochs with 8-bit quantization

| Parameter | Value |
|-----------|-------|
| Optimizer | Adam |
| Learning rate | 0.001 |
| Weight decay | 0.0001 |
| Validation interval | 2 epochs |
| Loss | MSE (time ×1.0 + polarity ×0.1) |

### 2. Preprocess Representations (optional)

Pre-compute and cache event representations to disk for faster detection training:

```bash
python preprocess_rep.py --config config/gen1.yaml
```

### 3. Train Object Detection

Trains YOLOX with a ResNet backbone on the selected representation:

```bash
python train.py --config config/gen1.yaml
```

| Parameter | Value |
|-----------|-------|
| Epochs | 100 |
| Warmup epochs | 5 |
| No-augmentation epochs | last 15 |
| Precision | 16-mixed |
| EMA decay | 0.9998 |
| Gradient clip | 1.0 |
| Metrics | mAP, mAP50, mAP75 |

---

## Configuration

Configs are in `config/` using OmegaConf YAML:

```yaml
# config/gen1.yaml (example)
name: Gen1
sensor_size: {W: 304, H: 240}
image_size: {W: 224, H: 224}
time_window: 200000        # microseconds
num_events: 50000

encoder:
  rnn_type: MyGRU
  hidden_size: [12, 12, 12]
  num_bits: 8              # quantization bits

representation: Encoder    # or ToImage, ToVoxelGrid, etc.
batch_size: 8
num_workers: 8
```

---

## Hardware (FPGA)

The `HW/` directory contains a Xilinx Vivado project implementing the quantized GRU encoder in RTL. The design uses:

- Distributed memory and arithmetic IP cores
- 8-bit fixed-point arithmetic matching the QAT model
- LUT-based sigmoid/tanh approximations

---

## Dataset

The code targets the **Gen1 Prophesee** event camera dataset (304×240 resolution). Data is stored in HDF5 format and loaded lazily via `h5py`. Experiment tracking is handled by [Weights & Biases](https://wandb.ai).

If you find the resources usefull, please cite the paper:


```
@inproceedings{jeziorek2025self,
  title={Self-supervised event representations: towards accurate, real-time perception on SoC FPGAs},
  author={Jeziorek, Kamil and Kryjak, Tomasz},
  booktitle={Real-time Processing of Image, Depth, and Video Information 2025},
  volume={13526},
  pages={1352602},
  year={2025},
  organization={SPIE}
}
```