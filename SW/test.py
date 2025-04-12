import torch
import torch.nn as nn

from models.my_gru import MyGRUCell

# torch.manual_seed(1)

model = MyGRUCell(input_size=2, hidden_size=12, num_bits=16)

x = torch.randn(1, 2)  # Batch size of 5, input size of 10
h = torch.randn(1, 12)  # Batch size of 5, hidden size of 20

for i in range(10):
    x = torch.randn(1, 2)  # Batch size of 5, input size of 10
    h = torch.randn(1, 12)  # Batch size of 5, hidden size of 20
    model.calibrate(x, h)



for i in range(1000):
    x = torch.randn(1, 2)  # Batch size of 5, input size of 10
    h = torch.randn(1, 12)  # Batch size of 5, hidden size of 20
    # Forward pass
    new_h1 = model(x, h)
    new_h2 = model.calibrate(x, h)
    new_h3 = model.qforward(x, h)

    diff1 = new_h1 - new_h3

    if diff1.abs().max() > 0.01:
        print('new_h1:', new_h1)
        print('new_h2:', new_h3)
        print(f"diff1: {diff1}")