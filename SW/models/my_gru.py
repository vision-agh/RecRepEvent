import math
import torch
import torch.nn as nn
import torch.nn.functional as F

from utils.observer import Observer, FakeQuantize, quantize_tensor, dequantize_tensor


class MyGRUCell(nn.Module):
    def __init__(self, 
                 input_size:int, 
                 hidden_size:int,
                 num_bits:int = 8):
        super(MyGRUCell, self).__init__()
        """
        Initialize the GRU cell with input size and hidden size.
        Args:
            input_size (int): Size of the input features.
            hidden_size (int): Size of the hidden state.
        """

        self.input_size = input_size
        self.hidden_size = hidden_size

        # GRU weights
        self.linear_ih = nn.Linear(input_size, 3 * hidden_size)
        self.linear_hh = nn.Linear(hidden_size, 3 * hidden_size)

        # Initialize weights
        self.reset_parameters()

        # Observers for quantization
        self.input_observer = Observer(num_bits=num_bits)
        self.hidden_observer = Observer(num_bits=num_bits)

        self.weight_ih_observer = Observer(num_bits=num_bits)
        self.weight_hh_observer = Observer(num_bits=num_bits)

        self.output_linear_observer = Observer(num_bits=num_bits)

        # Observer for sigmoid
        self.output_observer_sigmoid_r = Observer(num_bits=num_bits)
        self.output_observer_sigmoid_z = Observer(num_bits=num_bits)

        # Observer for tanh
        self.output_observer_tanh_n = Observer(num_bits=num_bits)

        self.register_buffer('lut_sigmoid_r', 
                                torch.zeros(2**(num_bits+1), dtype=torch.float32))
        self.register_buffer('lut_sigmoid_z',
                                torch.zeros(2**(num_bits+1), dtype=torch.float32))
        self.register_buffer('lut_tanh_n',
                                torch.zeros(2**(num_bits+1), dtype=torch.float32))

        # Observer for r * h_n
        self.output_observer_r_hn = Observer(num_bits=num_bits)

        # Observer for z * n
        self.output_observer_z_n = Observer(num_bits=num_bits)

        # Observer for z * h
        self.output_observer_z_h = Observer(num_bits=num_bits)

    def reset_parameters(self) -> None:
        """
        Initialize the parameters of the GRU cell.
        This is done using a uniform distribution.
        """
        std = 1.0 / math.sqrt(self.hidden_size)
        for w in self.parameters():
            w.data.uniform_(-std, std)

    def forward(self, 
                x: torch.Tensor, 
                h: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the GRU cell.
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, input_size).
            h (torch.Tensor): Hidden state tensor of shape (batch_size, hidden_size).
        Returns:
            torch.Tensor: New hidden state tensor of shape (batch_size, hidden_size).
        """

        assert x.size(1) == self.input_size,    "Input size mismatch"
        assert h.size(1) == self.hidden_size,   "Hidden size mismatch"
        assert x.size(0) == h.size(0),          "Batch size mismatch"

        # GRU cell computation
        gate_x = self.linear_ih(x)
        gate_h = self.linear_hh(h)

        # Split the gates
        i_r, i_z, i_n = gate_x.chunk(3, 1)
        h_r, h_z, h_n = gate_h.chunk(3, 1)

        # Reset gate
        r = torch.sigmoid(i_r + h_r)

        # Update gate
        z = torch.sigmoid(i_z + h_z)

        # New gate
        n = torch.tanh(i_n + r * h_n)

        # Final output
        new_h = (1 - z) * n + z * h
        return new_h
    
    def calibrate(self, 
                  x: torch.Tensor, 
                  h: torch.Tensor) -> None:
        """
        Calibrate the GRU cell with input and hidden state.
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, input_size).
            h (torch.Tensor): Hidden state tensor of shape (batch_size, hidden_size).
        """
        # Update observers with the input and hidden state
        self.input_observer.update(x)
        self.hidden_observer.update(h)

        x = FakeQuantize.apply(x, self.input_observer)
        h = FakeQuantize.apply(h, self.hidden_observer)

        # Update observers with the weights
        self.weight_ih_observer.update(self.linear_ih.weight)
        self.weight_hh_observer.update(self.linear_hh.weight)

        q_weight_ih = FakeQuantize.apply(self.linear_ih.weight, self.weight_ih_observer)
        q_weight_hh = FakeQuantize.apply(self.linear_hh.weight, self.weight_hh_observer)

        gate_x = F.linear(x, q_weight_ih, self.linear_ih.bias)
        gate_h = F.linear(h, q_weight_hh, self.linear_hh.bias)

        # Update observers with the output
        self.output_linear_observer.update(gate_x)
        self.output_linear_observer.update(gate_h)

        q_gate_x = FakeQuantize.apply(gate_x, self.output_linear_observer)
        q_gate_h = FakeQuantize.apply(gate_h, self.output_linear_observer)

        # Split the gates
        i_r, i_z, i_n = q_gate_x.chunk(3, 1)
        h_r, h_z, h_n = q_gate_h.chunk(3, 1)

        # Reset gate
        r = self.output_linear_observer.quantize_tensor(i_r) \
             + self.output_linear_observer.quantize_tensor(h_r) \
             - self.output_linear_observer.zero_point
        
        in_vec = torch.arange(0, 2**(self.output_linear_observer.num_bits+1), dtype=torch.float32)
        in_vec = dequantize_tensor(in_vec,
                                self.output_linear_observer.scale, 
                                self.output_linear_observer.zero_point)
        sigmoid_r = torch.sigmoid(in_vec)
        self.output_observer_sigmoid_r.update(sigmoid_r)
        self.lut_sigmoid_r = self.output_observer_sigmoid_r.quantize_tensor(sigmoid_r)
        sigmoid_r = FakeQuantize.apply(sigmoid_r, self.output_observer_sigmoid_r)

        r = sigmoid_r[r.long()]

        # Update gate
        z = self.output_linear_observer.quantize_tensor(i_z) \
             + self.output_linear_observer.quantize_tensor(h_z) \
             - self.output_linear_observer.zero_point
        
        in_vec = torch.arange(0, 2**(self.output_linear_observer.num_bits+1), dtype=torch.float32)
        in_vec = dequantize_tensor(in_vec,
                                self.output_linear_observer.scale, 
                                self.output_linear_observer.zero_point)
        sigmoid_z = torch.sigmoid(in_vec)
        self.output_observer_sigmoid_z.update(sigmoid_z)
        self.lut_sigmoid_z = self.output_observer_sigmoid_z.quantize_tensor(sigmoid_z)
        sigmoid_z = FakeQuantize.apply(sigmoid_z, self.output_observer_sigmoid_z)

        z = sigmoid_z[z.long()]

        # New gate multiplication
        r_hn = r * h_n
        self.output_observer_r_hn.update(r_hn)
        r_hn = FakeQuantize.apply(r_hn, self.output_observer_r_hn)

        # New gate intermediate computation
        i_n = self.output_linear_observer.quantize_tensor(i_n)
        i_n = i_n - self.output_linear_observer.zero_point
        i_n = (i_n * (self.output_linear_observer.scale / self.output_observer_r_hn.scale)).round()
        i_n = i_n + self.output_observer_r_hn.zero_point
        i_n = i_n.clamp(0, 2**self.output_observer_r_hn.num_bits - 1)
        i_n = self.output_observer_r_hn.dequantize_tensor(i_n)

        n = r_hn + i_n
        
        # New gate
        n = self.output_observer_r_hn.quantize_tensor(n)
        
        in_vec = torch.arange(0, 2**(self.output_observer_r_hn.num_bits+1), dtype=torch.float32)
        in_vec = dequantize_tensor(in_vec,
                                self.output_observer_r_hn.scale, 
                                self.output_observer_r_hn.zero_point)
        tanh_n = torch.tanh(in_vec)
        self.output_observer_tanh_n.update(tanh_n)
        tanh_n = FakeQuantize.apply(tanh_n, self.output_observer_tanh_n)
        self.lut_tanh_n = self.output_observer_tanh_n.quantize_tensor(tanh_n)

        n = tanh_n[n.long()]

        # New hidden state
        # Difference
        diff = quantize_tensor(1,
                                scale=self.output_observer_sigmoid_z.scale,
                                zero_point=self.output_observer_sigmoid_z.zero_point,
                                num_bits=self.output_observer_sigmoid_z.num_bits+1)
        
        diff = dequantize_tensor(diff,
                                self.output_observer_sigmoid_z.scale, 
                                self.output_observer_sigmoid_z.zero_point)
        
        z_diff = diff - z
        z_diff = FakeQuantize.apply(z_diff, self.output_observer_sigmoid_z)

        # Hammard product (1-z) * n
        z_n = z_diff * n
        self.output_observer_z_n.update(z_n)
        z_n = FakeQuantize.apply(z_n, self.output_observer_z_n)

        # Hammard product z * h
        z_h = z * h
        self.output_observer_z_h.update(z_h)
        z_h = FakeQuantize.apply(z_h, self.output_observer_z_h)

        new_h = z_n + z_h
        self.hidden_observer.update(new_h)
        new_h = FakeQuantize.apply(new_h, self.hidden_observer)

        return new_h

    def qforward(self, 
                 x: torch.Tensor, 
                 h: torch.Tensor) -> torch.Tensor:
        """
        Quantized forward pass of the GRU cell.
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, input_size).
            h (torch.Tensor): Hidden state tensor of shape (batch_size, hidden_size).
        Returns:
            torch.Tensor: New hidden state tensor of shape (batch_size, hidden_size).
        """
        # Quantize the input and hidden state
        x = self.input_observer.quantize_tensor(x)
        h = self.hidden_observer.quantize_tensor(h)

        # Quantize the weights and compute the input layer

        # Weights quantization
        q_weight_ih = self.weight_ih_observer.quantize_tensor(self.linear_ih.weight) \
                        - self.weight_ih_observer.zero_point
        q_bias_ih = quantize_tensor(self.linear_ih.bias, 
                                    scale=self.weight_ih_observer.scale * self.input_observer.scale,
                                    zero_point=0,
                                    num_bits=32,
                                    signed=True)

        scale_ih = (self.weight_ih_observer.scale * self.input_observer.scale) \
                    / self.output_linear_observer.scale
        
        # Compute the input layer
        gate_x = F.linear(x - self.input_observer.zero_point, 
                            q_weight_ih, 
                            q_bias_ih)

        gate_x = (gate_x * scale_ih).round()
        gate_x = gate_x + self.output_linear_observer.zero_point
        gate_x = gate_x.clamp(0, 2**self.output_linear_observer.num_bits - 1)

        # Quantize the weights and compute the hidden layer

        # Weights quantization
        q_weight_hh = self.weight_hh_observer.quantize_tensor(self.linear_hh.weight) \
                        - self.weight_hh_observer.zero_point
        q_bias_hh = quantize_tensor(self.linear_hh.bias, 
                                    scale=self.weight_hh_observer.scale * self.hidden_observer.scale,
                                    zero_point=0,
                                    num_bits=32,
                                    signed=True)
        scale_hh = (self.weight_hh_observer.scale * self.hidden_observer.scale) \
                    / self.output_linear_observer.scale
        
        # Compute the hidden layer
        gate_h = F.linear(h - self.hidden_observer.zero_point, 
                            q_weight_hh, 
                            q_bias_hh)
        gate_h = (gate_h * scale_hh).round()
        gate_h = gate_h + self.output_linear_observer.zero_point
        gate_h = gate_h.clamp(0, 2**self.output_linear_observer.num_bits - 1)

        # Split the gates
        i_r, i_z, i_n = gate_x.chunk(3, 1)
        h_r, h_z, h_n = gate_h.chunk(3, 1)

        # Reset gate
        r = (i_r + h_r - self.output_linear_observer.zero_point).int()
        r = self.lut_sigmoid_r[r]

        # Update gate
        z = (i_z + h_z - self.output_linear_observer.zero_point).int()
        z = self.lut_sigmoid_z[z]

        # New gate multiplication
        scale_r_hn = (self.output_observer_sigmoid_r.scale * self.output_linear_observer.scale) \
                    / self.output_observer_r_hn.scale
        r_hn = (r-self.output_observer_sigmoid_r.zero_point) * (h_n - self.output_linear_observer.zero_point)
        r_hn = (r_hn * scale_r_hn).round()
        r_hn = r_hn + self.output_observer_r_hn.zero_point
        r_hn = r_hn.clamp(0, 2**self.output_observer_r_hn.num_bits - 1)

        # New gate
        scale_i_n = (self.output_linear_observer.scale) / self.output_observer_r_hn.scale 
        i_n = (i_n - self.output_linear_observer.zero_point)
        i_n = (i_n * scale_i_n).round()
        i_n = i_n + self.output_observer_r_hn.zero_point
        i_n = i_n.clamp(0, 2**self.output_observer_r_hn.num_bits - 1)

        n = r_hn + i_n - self.output_observer_r_hn.zero_point
        n = self.lut_tanh_n[n.int()]

        # New hidden state
        # Difference
        quant_1 = quantize_tensor(1,
                                scale=self.output_observer_sigmoid_z.scale,
                                zero_point=self.output_observer_sigmoid_z.zero_point,
                                num_bits=self.output_observer_sigmoid_z.num_bits+1)
        
        z_diff = quant_1 - z

        # Hammard product (1-z) * n
        scale_z_n = (self.output_observer_sigmoid_z.scale * self.output_observer_tanh_n.scale) \
                    / self.output_observer_z_n.scale
        z_n = (z_diff-self.output_observer_sigmoid_z.zero_point) * (n - self.output_observer_tanh_n.zero_point)
        z_n = (z_n * scale_z_n).round()
        z_n = z_n + self.output_observer_z_n.zero_point
        z_n = z_n.clamp(0, 2**self.output_observer_z_n.num_bits - 1)

        # Hammard product z * h
        scale_z_h = (self.output_observer_sigmoid_z.scale * self.hidden_observer.scale) \
                    / self.output_observer_z_h.scale
        z_h = (z-self.output_observer_sigmoid_z.zero_point) * (h - self.hidden_observer.zero_point)
        z_h = (z_h * scale_z_h).round()
        z_h = z_h + self.output_observer_z_h.zero_point
        z_h = z_h.clamp(0, 2**self.output_observer_z_h.num_bits - 1)

        # New hidden state
        scale_new_h_zn = self.output_observer_z_n.scale / self.hidden_observer.scale
        scale_new_h_zh = self.output_observer_z_h.scale / self.hidden_observer.scale
        new_h = (z_n - self.output_observer_z_n.zero_point) * scale_new_h_zn \
                + (z_h - self.output_observer_z_h.zero_point) * scale_new_h_zh
        new_h = new_h.round()
        new_h = new_h + self.hidden_observer.zero_point
        new_h = new_h.clamp(0, 2**self.hidden_observer.num_bits - 1)

        return self.hidden_observer.dequantize_tensor(new_h)