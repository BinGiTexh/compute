# Build stage
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local /usr/local

# Set up working directory
WORKDIR /app

# Create input/output directories
RUN mkdir -p /app/input /app/output && \
    chmod 777 /app/input /app/output

# Copy application code
COPY test_resize.py /app/

# Set environment variables for CUDA
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV MAX_SIZE=512

# Default command with environment variable
CMD python3 test_resize.py \
    --input_dir /app/input \
    --output_dir /app/output \
    --max_size $MAX_SIZE
