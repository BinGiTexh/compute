FROM nvcr.io/nvidia/pytorch:24.05-py3

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    libopenblas-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Install Boltz from GitHub
WORKDIR /app
RUN git clone https://github.com/jwohlwend/boltz.git
WORKDIR /app/boltz
RUN pip3 install --no-cache-dir -e .

# Install additional dependencies
RUN pip3 install --no-cache-dir \
    scipy \
    matplotlib \
    pandas \
    jupyter \
    jupyterlab \
    biopython \
    scikit-learn \
    h5py \
    tqdm

# Create workspace directory for data and outputs
RUN mkdir -p /workspace
WORKDIR /workspace

# Set environment variables for GPU usage
ENV CUDA_VISIBLE_DEVICES=0
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Expose ports for JupyterLab and potential API services
EXPOSE 8888

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command to run JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]

