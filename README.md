# Jetson Segmentation Pipeline for CoralScapes

A GPU-accelerated semantic segmentation pipeline for processing coral imagery on NVIDIA Jetson devices. This implementation uses the Segformer model fine-tuned on the CoralScapes dataset.

## Features

- Optimized for Jetson devices
- GPU-accelerated image processing
- Memory-efficient implementation
- Automated deployment via GitHub Actions
- Docker containerization for reproducibility
- Built-in image resizing for memory management

## Directory Structure

```
jetson-segmentation-pipeline/
├── scripts/
│   ├── test_resize.py    # Main processing script
│   ├── Dockerfile        # Container configuration
│   └── requirements.txt  # Python dependencies
├── input/               # Input images directory
├── output/              # Output predictions directory
├── docs/                # Documentation
└── .github/             # GitHub Actions workflows
```

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

1. Clone this repository:
```bash
git clone https://github.com/BinGiTexh/compute.git
cd compute/jetson-segmentation-pipeline
```

2. Build the Docker image:
```bash
docker build -t coralscapes-test:latest scripts/
```

3. Run the container:
```bash
docker run --gpus all \
    -v $(pwd)/input:/app/input \
    -v $(pwd)/output:/app/output \
    --memory=8g \
    --memory-swap=16g \
    --shm-size=1g \
    coralscapes-test:latest
```

## Jetson Setup Requirements

- NVIDIA Jetson device with JetPack 5.0+
- Docker and NVIDIA Container Runtime
- GitHub Actions self-hosted runner
- Python 3.11+

## GitHub Actions Integration

The workflow automatically:
- Builds the Docker image
- Processes images using the Segformer model
- Uploads results as artifacts

Triggers:
- Push to main branch
- Pull requests
- Manual workflow dispatch

## Performance Considerations

- Image processing speed: ~1.88 seconds per image
- Memory usage optimized for Jetson devices
- Automatic CUDA acceleration
- Dynamic image resizing for memory efficiency

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
