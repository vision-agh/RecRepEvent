import torch
import lightning as L
import wandb 
import numpy as np

from models.recurrent.encoder import Encoder
from models.recurrent.decoder import Decoder

class AutoEncoder(L.LightningModule):
    def __init__(self, cfg):
        super(AutoEncoder, self).__init__()
 
        self.cfg = cfg

        self.encoder = Encoder(input_size=2, hidden_size=12, num_bits=8, input_num_bits=12)
        self.decoder = Decoder(hidden_size=12, output_size=2)

        self.encoder.compile()
        self.decoder.compile()

        self.loss_time = torch.nn.MSELoss(reduction='none')
        self.loss_polarity = torch.nn.MSELoss(reduction='none')

        self.lr = cfg['train_encoder']['learning_rate']
        self.weight_decay = cfg['train_encoder']['weight_decay']

        self.calibrate = False

    def forward(self, batch):
        events = batch['packed_events'][0]
        mask = batch['mask'][0]

        if self.calibrate:
            embeddings = self.encoder.calibrate(events)
        else:
            embeddings = self.encoder(events)

        output = self.decoder(embeddings, events.size(0))

        self.embedding = embeddings
        loss, loss_t, loss_p = self._loss_fun(events, output, mask=mask)
        return loss, loss_t, loss_p, events, output
    
    def _loss_fun(self, events, output, mask):
        # Calculate loss for time
        loss_t = self.loss_time(events[:, :, 0], output[:, :, 0])
        loss_t = loss_t[mask].sum() / mask.sum()

        # Calculate loss for polarity
        loss_p = self.loss_polarity(events[:, :, 1], output[:, :, 1])
        loss_p = loss_p[mask].sum() / mask.sum()

        loss = loss_t * self.cfg['train_encoder']['scale_time_loss'] \
             + loss_p * self.cfg['train_encoder']['scale_polarity_loss']
        
        return loss, loss_t, loss_p
    
    def training_step(self, batch, batch_idx):
        loss, loss_time, loss_pol, _, _ = self.forward(batch)
        self.log('train_loss', loss, batch_size=1)
        self.log('train_loss_time', loss_time, batch_size=1)
        self.log('train_loss_pol', loss_pol, batch_size=1)
        return loss
        
    def validation_step(self, batch, batch_idx):
        loss, loss_time, loss_pol, input, output = self.forward(batch)
        self.log('val_loss', loss, batch_size=1)
        self.log('val_loss_time', loss_time, batch_size=1)
        self.log('val_loss_pol', loss_pol, batch_size=1)
        return loss
    
    def test_step(self, batch, batch_idx):
        loss, loss_time, loss_pol  = self.forward(batch)
        self.log('test_loss', loss, batch_size=1)
        self.log('test_loss_time', loss_time, batch_size=1)
        self.log('test_loss_pol', loss_pol, batch_size=1)
        return loss
    
    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), 
                                        lr=self.lr,
                                        weight_decay=self.weight_decay)
        return optimizer