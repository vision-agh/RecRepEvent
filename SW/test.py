import torch
import torch.nn as nn

from models.my_gru import MyGRUCell

torch.manual_seed(0)

model = MyGRUCell(input_size=2, hidden_size=12, num_bits=16)

x = torch.randn(1, 2)  # Batch size of 5, input size of 10
h = torch.randn(1, 12)  # Batch size of 5, hidden size of 20

for i in range(10):
    x = torch.randn(1, 2)  # Batch size of 5, input size of 10
    h = torch.randn(1, 12)  # Batch size of 5, hidden size of 20
    model.calibrate(x, h)



print ("#" * 40)

# Forward pass
model(x, h)
print ("#" * 10)
model.calibrate(x, h)
print ("#" * 10)
model.qforward(x, h)