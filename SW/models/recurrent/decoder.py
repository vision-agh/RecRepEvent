import torch
import torch.nn as nn
from models.recurrent.my_layers.my_gru import MyGRUCell

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
            h3 = self.gru3(h2, h3)

            # decode event
            y_t = self.linear(h3)              # (B, output_size)
            out[t, :, :] = y_t                 # write into buffer

            # prepare next input by projecting back into hidden‐space
            x_in = self.output2hidden(y_t)     # (B, hidden_size)

        return out