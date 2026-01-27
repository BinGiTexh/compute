FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

# (optional) system packages …
RUN apt-get update && apt-get install -y git build-essential

# upgrade pip, but DO NOT touch torch / torchvision
RUN pip install -U pip setuptools wheel

# install Boltz and extras without pulling deps
WORKDIR /app
RUN git clone https://github.com/jwohlwend/boltz.git
WORKDIR /app/boltz
RUN pip install boltz -U

RUN pip install --no-cache-dir --no-deps \
 #   pytorch_lightning==2.2.* \
 #   lightning_utilities==0.11.* \
 #   torchmetrics==1.3.* \
 #   packaging \
    pyparsing \
    cycler \
    python-dateutil \
    kiwisolver \
    rdkit \
    typing_extensions \
 #   numba \
 #   llvmlite \
 #   einops \
 #   mashumaro \
    scipy matplotlib pandas jupyter jupyterlab \
    biopython scikit-learn h5py tqdm

# Create workspace directory for data and outputs
RUN mkdir -p /workspace
WORKDIR /workspace

# Set environment variables for GPU usage
ENV CUDA_VISIBLE_DEVICES=0
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Expose ports for JupyterLab and potential API services
EXPOSE 8888

#COPY entrypoint.sh /entrypoint.sh
#RUN chmod +x /entrypoint.sh

# Set the entrypoint
#ENTRYPOINT ["/entrypoint.sh"]

# Default command to run JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
