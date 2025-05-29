FROM nvcr.io/nvidia/l4t-ml:r35.2.1-py3

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Create directories
RUN mkdir -p /models /data

# Copy inference server code
COPY . /app
WORKDIR /app

# Environment variables
ENV MODEL_DIR=/models
ENV INFERENCE_SERVER_PORT=9001

# Expose port
EXPOSE 9001

# Start inference server
CMD ["python3", "server.py"]
