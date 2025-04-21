Build and run docker:

'''
docker build -t rec-rep .
docker run -it --rm --gpus all -v $(pwd):/workspace -w /workspace my-dev-env
'''


The equations for the GRU cell are as follows:
```latex
\begin{align*}
r_t &= \sigma(W_{ir} x_t + b_{ir} + W_{hr} h_{(t-1)} + b_{hr}) \\
z_t &= \sigma(W_{iz} x_t + b_{iz} + W_{hz} h_{(t-1)} + b_{hz}) \\
n_t &= \tanh(W_{in} x_t + b_{in} + r_t \odot (W_{hn} h_{(t-1)}+ b_{hn})) \\
h_t &= (1 - z_t) \odot n_t + z_t \odot h_{(t-1)}
\end{align*}
```

Where:
- \(x_t\) is the input at time step \(t\)
- \(h_{(t-1)}\) is the hidden state from the previous time step
- \(h_t\) is the hidden state at time step \(t\)
- \(W_{ir}, W_{iz}, W_{in}, W_{hr}, W_{hz}, W_{hn}\) are the weight matrices for the input and hidden states
- \(b_{ir}, b_{iz}, b_{in}, b_{hr}, b_{hz}, b_{hn}\) are the bias vectors
- \(r_t\) is the reset gate
- \(z_t\) is the update gate
- \(n_t\) is the new memory content
- \(\sigma\) is the sigmoid activation function





conda create -n dvs_rec python=3.12
pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
conda install h5py 
conda install blosc-hdf5-plugin lightning -c conda-forge
