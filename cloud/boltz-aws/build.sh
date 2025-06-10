#!/bin/bash

# Get system architecture and CUDA version
ARCH=$(uname -m)
CUDA_VERSION="12.4"

# Add timestamp for versioning
TIMESTAMP=$(date +%Y%m%d)

# Set tag with architecture, CUDA version and timestamp
TAG="boltz-${ARCH}-cuda${CUDA_VERSION}-${TIMESTAMP}-test"

# Print build information
echo "Building Boltz container for:"
echo "  Architecture: ${ARCH}"
echo "  CUDA Version: ${CUDA_VERSION}"
echo "  Base Image: nvcr.io/nvidia/pytorch:24.05-py3"
echo "  Tag: ${TAG}"
echo ""

# Create required directories if they don't exist
mkdir -p data models examples

# Build the Docker image
docker build -f Dockerfile -t ${TAG} .

# Print success message
echo ""
echo "Build complete!"
echo "To run the container:"
echo "docker run --gpus all -it --rm -p 8888:8888 \
  -v $(pwd)/data:/workspace/data \
  -v $(pwd)/models:/workspace/models \
  -v $(pwd)/examples:/workspace/examples \
  ${TAG}"

echo ""
echo "To push to a registry (if needed):"
echo "docker tag ${TAG} your-registry/${TAG}"
echo "docker push your-registry/${TAG}"

