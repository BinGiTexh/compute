# Jetson Segmentation Pipeline for CoralScapes

A GPU-accelerated semantic segmentation pipeline for processing coral imagery on NVIDIA Jetson devices. This implementation uses the Segformer model fine-tuned on the CoralScapes dataset.

## Features

- Optimized for Jetson devices
- GPU-accelerated image processing
- Memory-efficient implementation
- Automated deployment via GitHub Actions
- Docker containerization for reproducibility
- Built-in image resizing for memory management

## Technical Specifications

- **Base Image**: Python 3.11-slim
- **Deep Learning Model**: Segformer-B5 (EPFL-ECEO/segformer-b5-finetuned-coralscapes-1024-1024)
- **Processing Capacity**: ~1.88 seconds per image
- **Memory Management**:
  - 8GB container memory limit
  - 16GB swap space
  - 1GB shared memory
  - Dynamic image resizing (max 512px)

## Quick Start

1. Build the Docker image:
```bash
cd scripts
docker build -t coralscapes-test:latest .
```

2. Run the container:
```bash
docker run --gpus all \
    -v /path/to/input:/app/input \
    -v /path/to/output:/app/output \
    --memory=8g \
    --memory-swap=16g \
    --shm-size=1g \
    coralscapes-test:latest
```

## Requirements

- NVIDIA Jetson device with JetPack 5.0+
- Docker and NVIDIA Container Runtime
- Python 3.11+

## Documentation

See the `docs` directory for detailed information on:
- Setup and installation
- Performance optimization
- Troubleshooting
- GitHub Actions configuration
