# fft-conv-pytorch

Implementation of 1D, 2D, and 3D FFT convolutions in PyTorch.  
* Faster than direct convolution for large kernels.
* **Much slower** than direct convolution for small kernels.
* In my local tests, FFT convolution is faster when the kernel has >100 or so elements.
    * Dependent on machine and PyTorch version.
    * Also see benchmarks below.


## Install

Using `pip`:
```bash
pip install fft-conv-pytorch
```

From source:
```bash
git clone https://github.com/fkodom/fft-conv-pytorch.git
cd fft-conv-pytorch
pip install .
```

## Example Usage

```python
import torch
from fft_conv_pytorch import fft_conv, FFTConv1d

# Create dummy data.  
#     Data shape: (batch, channels, length)
#     Kernel shape: (out_channels, in_channels, kernel_size)
#     Bias shape: (out channels, )
# For ordinary 1D convolution, simply set batch=1.
signal = torch.randn(3, 3, 1024 * 1024)
kernel = torch.randn(2, 3, 128)
bias = torch.randn(2)

# Functional execution.  (Easiest for generic use cases.)
out = fft_conv(signal, kernel, bias=bias)

# Object-oriented execution.  (Requires some extra work, since the 
# defined classes were designed for use in neural networks.)
fft_conv = FFTConv1d(3, 2, 128, bias=True)
fft_conv.weight = torch.nn.Parameter(kernel)
fft_conv.bias = torch.nn.Parameter(bias)
out = fft_conv(signal)
```

## Benchmarks

Benchmarking FFT convolution against the direct convolution from PyTorch in 1D, 2D, 
and 3D. The exact times are heavily dependent on your local machine, but relative 
scaling with kernel size is always the same. 

Dimensions | Input Size   | Input Channels | Output Channels | Bias | Padding | Stride | Dilation
-----------|--------------|----------------|-----------------|------|---------|--------|---------
1          | (4096)       | 4              | 4               | True | 0       | 1      | 1
2          | (512, 512)   | 4              | 4               | True | 0       | 1      | 1
3          | (64, 64, 64) | 4              | 4               | True | 0       | 1      | 1

![Benchmark Plot](doc/benchmark.png)