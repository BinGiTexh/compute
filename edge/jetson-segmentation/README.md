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

## Secure Image Upload Guide

There are two secure methods to upload images for processing:

### 1. Direct Artifact Upload (for smaller datasets)
1. Go to Actions > "Process Uploaded Images"
2. Click "Run workflow"
3. Choose "artifact" as upload type
4. Upload your images through the GitHub UI
5. The workflow will process them automatically

### 2. Encrypted Release Upload (for larger datasets)
1. Install the encryption tool:
```bash
pip install cryptography
```

2. Encrypt your zip file:
```bash
# Get encryption key from repository secrets
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Encrypt your zip file
python3 scripts/utils/encrypt_file.py input_images.zip encrypted_images.zip YOUR_ENCRYPTION_KEY
```

3. Create a new release with the encrypted file
4. Go to Actions > "Process Uploaded Images"
5. Choose "release" as upload type
6. Enter the release tag
7. (Optional) Provide the SHA-256 checksum

The workflow will:
1. Download the encrypted file
2. Verify the checksum (if provided)
3. Decrypt and process the images
4. Run the segmentation pipeline
5. Upload results as artifacts

### Security Considerations
- Images are encrypted during upload
- Checksums verify file integrity
- Automatic cleanup after processing
- Secure key management through GitHub Secrets
