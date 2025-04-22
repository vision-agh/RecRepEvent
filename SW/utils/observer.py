import math
import torch
import torch.nn as nn
from torch.autograd import Function


def quantize_tensor(tensor, 
                    scale, 
                    zero_point, 
                    num_bits=8,
                    signed=False):
    """
    Quantize tensor: float -> int.
    """
    if signed:
        qmin = -2**(num_bits - 1)
        qmax = 2**(num_bits - 1) - 1
    else:
        qmin = 0
        qmax = 2**num_bits - 1

    q_tensor = torch.round(tensor / (scale + 1e-8) + zero_point)
    q_tensor = torch.clamp(q_tensor, qmin, qmax)
    return q_tensor

def dequantize_tensor(tensor, scale, zero_point):
    """
    Dequantize tensor: int -> float.
    """
    return (tensor - zero_point) * scale

class Observer(nn.Module):
    def __init__(self, 
                 num_bits:int = 8):
        super().__init__()
        self.num_bits = num_bits
        '''Initialize parameters for quantization'''
        self.register_buffer('scale', torch.tensor(0.0, requires_grad=False))
        self.register_buffer('zero_point', torch.tensor(0.0, requires_grad=False))
        self.register_buffer('min', torch.tensor(float('inf'), requires_grad=False))
        self.register_buffer('max', torch.tensor(float('-inf'), requires_grad=False))

    def update(self, tensor: torch.Tensor):
        """
        Update min and max values for the tensor.
        This is used to calculate scale and zero point.
        """
        with torch.no_grad():
            tensor_min = torch.min(tensor).item()
            tensor_max = torch.max(tensor).item()
            self.min = torch.tensor(min(self.min.item(), tensor_min), device=tensor.device)
            self.max = torch.tensor(max(self.max.item(), tensor_max), device=tensor.device)

            if self.max > self.min:
                self.scale, self.zero_point = self.calcScaleZeroPoint()

    def quantize_tensor(self, tensor: torch.Tensor):
        """
        Quantize tensor using the scale and zero point.
        """
        return quantize_tensor(tensor, self.scale, self.zero_point, self.num_bits)
    
    def dequantize_tensor(self, tensor_quant: torch.Tensor):
        """
        Dequantize tensor using the scale and zero point.
        """
        return dequantize_tensor(tensor_quant, self.scale, self.zero_point)

    def calcScaleZeroPoint(self):
        """
        Calculate scale and zero point for quantization.
        """
        qmin = 0.
        qmax = 2**self.num_bits - 1
        scale = (self.max - self.min) / (qmax - qmin)
        zero_point = qmin - self.min / scale
        zero_point = torch.round(zero_point)
        zero_point = torch.clamp(zero_point, qmin, qmax)
        return scale, zero_point
    

class FakeQuantize(Function):
    '''Function for fake quantization.'''
    '''This function is used to calculate loss that occurs due to quantization.'''
    @staticmethod
    def forward(ctx, x, qparam):
        x = qparam.quantize_tensor(x)
        x = qparam.dequantize_tensor(x)
        return x

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output, None