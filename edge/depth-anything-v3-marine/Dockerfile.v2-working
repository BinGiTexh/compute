FROM dustynv/l4t-pytorch:2.2-r35.4.1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3-pip \
    v4l-utils \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set CUDA environment variables
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$CUDA_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
ENV CUDACXX=$CUDA_HOME/bin/nvcc

# Override pip configuration to use standard PyPI
RUN mkdir -p /root/.config/pip && \
    echo '[global]' > /root/.config/pip/pip.conf && \
    echo 'index-url = https://pypi.org/simple/' >> /root/.config/pip/pip.conf && \
    echo 'trusted-host = pypi.org' >> /root/.config/pip/pip.conf

# Install Python dependencies using standard PyPI
RUN pip3 install --no-cache-dir --index-url https://pypi.org/simple/ \
    "numpy<2.0" \
    transformers \
    torch \
    torchvision \
    timm \
    huggingface-hub \
    pillow \
    accelerate

# Create workspace
WORKDIR /workspace

# Copy our custom processing scripts
COPY turtle_depth_processor.py /workspace/
COPY run_analysis.py /workspace/
COPY process_frames.py /workspace/

# Create directories for models and output
RUN mkdir -p /workspace/models /workspace/output /workspace/videos /workspace/frames

# Set default command
CMD ["python3", "/workspace/run_analysis.py"]
