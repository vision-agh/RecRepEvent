import argparse
import torch
import yaml

from omegaconf import OmegaConf
from models.detection.resnet import ResNetDetectionModel
from data.gen1_2_encoder import Gen1
from models.recurrent.encoder import Encoder

from models.detection.utils.convert_bbox import convert_to_training_format
from utils.unpack_embeddings import unpack_embeddings

import torchvision.transforms as transforms
from time import time

with open("config/general.yaml", 'r') as file:
    config = yaml.safe_load(file)

config["remove_empty_pixels"] = False
config["crop_events_spatially"] = False

dm = Gen1(cfg=config)
dm.setup()


cfg = OmegaConf.create({
    "channels": 12,
    "num_classes": 2,
    "weights": None})

enc = Encoder(input_size=2, hidden_size=12, num_bits=8).eval().cuda()
enc.compile()

checkpoint = torch.load("checkpoints/my_gru_checkpoint-v7.ckpt", weights_only=True)
encoder_weights = {k.replace("encoder.", ""): v for k, v in checkpoint["state_dict"].items() if k.startswith("encoder.")}
enc.load_state_dict(encoder_weights, strict=False)

model = ResNetDetectionModel(cfg, num_classes=2).cuda()
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.0001)
optimizer_enc = torch.optim.AdamW(enc.parameters(), lr=0.001, weight_decay=0.0001)

print("1", torch.cuda.memory_allocated() / 1024 ** 2)

for i, batch in enumerate(dm.val_dataloader()):

    t1 = time()
    events = batch['packed_events']
    counts_per_pixel = batch['counts_per_pixel']
    bboxes = batch['bboxes']
    batch_bbox = batch['batch_bbox']
    
    batch_embeddings = []
    for ev, count in zip(events, counts_per_pixel):

        embeddings = enc(ev.cuda()).cpu()

        u_embeddings = unpack_embeddings(embeddings, 
                                        config["sensor_size"]["H"], 
                                        config["sensor_size"]["W"],
                                        count)
        
        batch_embeddings.append(u_embeddings)
    
    batch_embeddings = torch.stack(batch_embeddings, dim=0)
    batch_embeddings = transforms.Resize((224, 224))(batch_embeddings)

    bboxes[:, 0] = bboxes[:, 0] / config["sensor_size"]["W"] * 224
    bboxes[:, 1] = bboxes[:, 1] / config["sensor_size"]["H"] * 224
    bboxes[:, 2] = bboxes[:, 2] / config["sensor_size"]["W"] * 224
    bboxes[:, 3] = bboxes[:, 3] / config["sensor_size"]["H"] * 224

    target = convert_to_training_format(bboxes.float(), batch_bbox, 8)

    preds = model(batch_embeddings.cuda(), target.cuda())

    loss = preds["total_loss"]

    optimizer.zero_grad()
    optimizer_enc.zero_grad()
    loss.backward()
    optimizer.step()
    optimizer_enc.step()

    print(time() - t1)
    print(enc.gru1.linear_ih.bias)
    print(loss)