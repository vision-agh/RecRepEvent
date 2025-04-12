FROM pytorch/pytorch:2.4.1-cuda12.4-cudnn9-devel

# install cugraph
RUN pip install torch_geometric
RUN pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.4.0+cu124.html
RUN pip install lightning wandb

CMD [ "bash" ]