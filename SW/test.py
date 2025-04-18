import torch
import torch.nn as nn

from models.my_gru import MyGRUCell

torch.manual_seed(1)

model = MyGRUCell(input_size=1, hidden_size=12, num_bits=8).eval()

for i in range(10):
    x = torch.randn(1, 1)  # Batch size of 5, input size of 10
    h = torch.randn(1, 12)  # Batch size of 5, hidden size of 20
    model.calibrate(x, h)


print(model.state_dict())
x = torch.randn(1, 1)  # Batch size of 5, input size of 10
h = torch.zeros(1, 12)  # Batch size of 5, hidden size of 20
h1 = h.clone()
h2 = model.hidden_observer.quantize_tensor(h)

print(x)
print(h2)

for i in range(20):
    # Forward pass
    h = model(x, h)
    h1 = model.calibrate(x, h1)
    h2 = model.qforward(x, h2)
    h2_print = model.hidden_observer.dequantize_tensor(h2)

    print("##############################")
    print("Float32", h)
    print("Quant", h1)
    print("Quant", h2_print)

