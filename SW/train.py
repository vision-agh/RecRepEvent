import numpy as np
import torch
import torch.nn as nn

from models.my_layers.my_gru import MyGRUCell
from models.encoder import Encoder
from utils.pack_events import pack_events_parallel
from time import time

torch.manual_seed(1)



class Decoder(nn.Module):
    def __init__(self, hidden_size: int, output_size: int):
        super(Decoder, self).__init__()
        self.hidden_size  = hidden_size
        self.output_size  = output_size

        # three-layer GRU stack, all states in hidden_size
        self.gru1 = MyGRUCell(hidden_size, hidden_size)
        self.gru2 = MyGRUCell(hidden_size, hidden_size)
        self.gru3 = MyGRUCell(hidden_size, hidden_size)

        # from top hidden to events
        self.linear         = nn.Linear(hidden_size, output_size)
        # map events back into hidden‐space for the next step
        self.output2hidden  = nn.Linear(output_size, hidden_size)

    def compile(self):
        return torch.jit.script(self)

    def forward(self, 
                x: torch.Tensor,
                length: int,
                ) -> torch.Tensor:
        """
        Args:
          x:      (B, H)  — the encoder’s final hidden state; initial 
                          “input” to the decoder
          length:       int — how many events to decode

        Returns:
          out:   (B, length, output_size)
        """
        B = x.size(0)
        device = x.device

        # initialize all GRU hidden states to zero
        h1 = torch.zeros(B, self.hidden_size, device=device)
        h2 = torch.zeros(B, self.hidden_size, device=device)
        h3 = torch.zeros(B, self.hidden_size, device=device)

        # buffer to collect all outputs
        out = torch.zeros(length, B, self.output_size, device=device)

        # autoregressive loop
        x_in = x
        for t in range(length):
            # update each GRU layer
            h1 = self.gru1(x_in, h1)
            h2 = self.gru2(h1, h2)
            # h3 = self.gru3(h2, h3)

            # decode event
            y_t = self.linear(h2)              # (B, output_size)
            out[t, :, :] = y_t                 # write into buffer

            # prepare next input by projecting back into hidden‐space
            x_in = self.output2hidden(y_t)     # (B, hidden_size)

        return out
    
# Inicjalizacja modelu i wejścia
encoder = Encoder(input_size=1, hidden_size=12, num_bits=8).cuda()
decoder = Decoder(hidden_size=12, output_size=1).cuda()
encoder = encoder.compile()
decoder = decoder.compile()

# model.eval()
events = torch.from_numpy(np.loadtxt('events.txt')).float()
mask = (events[:, 0] > 0.0) & (events[:, 0] < 0.05)
events = events[mask]

packed_events, counts_per_pixel, mask = pack_events_parallel(events, 346, 260, include_polarity=False)
data = packed_events[:, counts_per_pixel > 0, :]  # (L, N, D)
mask = mask[:, counts_per_pixel > 0]  # (L, N)

data = data.cuda()

loss = torch.nn.MSELoss(reduction='none')
optimizer = torch.optim.AdamW(list(encoder.parameters()) + list(decoder.parameters()), lr=0.0001)

for i in range(1000):
    B = data.size(1)
    H = 12
    device = data.device
    h1 = torch.zeros(B, H, device=device)
    h2 = torch.zeros(B, H, device=device)
    h3 = torch.zeros(B, H, device=device)

    out = encoder(data, h1, h2, h3)
    out1 = decoder(out, data.size(0))
    err = loss(out1, data)

    total_loss = err[mask].sum() / mask.sum()
    print("Total loss:", total_loss.item())

    # backward pass
    total_loss.backward()

    # update weights
    optimizer.step()
