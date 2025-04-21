import torch
import torch.nn as nn
from models.my_layers.my_gru import MyGRUCell
from models.my_layers.my_ligru import MyLiGRUCell
from models.my_layers.my_mgu import MyMGUCell

class Encoder(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_bits: int):
        super(Encoder, self).__init__()
        self.hidden_size = hidden_size

        self.gru1 = MyMGUCell(input_size, hidden_size, num_bits)
        self.gru2 = MyMGUCell(hidden_size, hidden_size, num_bits)
        self.gru3 = MyMGUCell(hidden_size, hidden_size, num_bits)

    def forward(
        self,
        x: torch.Tensor,
        h1: torch.Tensor = None,
        h2: torch.Tensor = None,
        h3: torch.Tensor = None,
    ) -> torch.Tensor:
        
        if h1 is None:
            h1 = torch.zeros(x.size(1), self.hidden_size, device=x.device)
        if h2 is None:
            h2 = torch.zeros(x.size(1), self.hidden_size, device=x.device)
        if h3 is None:
            h3 = torch.zeros(x.size(1), self.hidden_size, device=x.device)
        
        # x: (L, B, D), h1/h2: (B, H)

        for l in range(x.size(0)):
            x_in = x[l, :, :]
            h1 = self.gru1(x_in, h1)
            h2 = self.gru2(h1, h2)
            h3 = self.gru3(h2, h3)
        return h3
    
    def compile(self):
        return torch.jit.script(self)
    