#!/bin/bash

# Exit on error
set -e

echo "Setting up Video Processing Pipeline..."

# Check for required tools
check_requirement() {
    if ! command -v $1 &> /dev/null; then
        echo "Error: $1 is required but not installed."
        echo "Please install $1 and try again."
        exit 1
    fi
}

check_requirement docker
check_requirement docker-compose
check_requirement python3
check_requirement git

# Check for NVIDIA runtime
if ! docker info | grep -i "nvidia" &> /dev/null; then
    echo "Warning: NVIDIA Container Runtime not found."
    echo "GPU acceleration may not be available."
fi

# Create required directories
mkdir -p models output

# Check for environment variables
if [ -z "$ROBOFLOW_API_KEY" ]; then
    echo "Warning: ROBOFLOW_API_KEY environment variable not set"
    echo "Please set it before running the pipeline:"
    echo "export ROBOFLOW_API_KEY=your_key_here"
fi

# Build Docker images
echo "Building Docker images..."
docker compose build

# Download default model
if [ ! -z "$ROBOFLOW_API_KEY" ]; then
    echo "Downloading default model..."
    python3 scripts/download_model.py --model-id "fish-scuba-project/2"
fi

# Create test video
echo "Creating test video..."
python3 tests/test_video.py

# Start services
echo "Starting services..."
docker compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check service health
if curl -f http://localhost:9001/health &> /dev/null; then
    echo "Inference server is running"
else
    echo "Warning: Inference server may not be running properly"
fi

if curl -f http://localhost:8888 &> /dev/null; then
    echo "JupyterLab is running"
else
    echo "Warning: JupyterLab may not be running properly"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To use the pipeline:"
echo "1. Access JupyterLab at http://localhost:8888"
echo "2. Open notebooks/templates/video_analysis_template.ipynb"
echo "3. Process a video using:"
echo "   python3 scripts/process_video.py --config configs/default_config.yaml --video path/to/video.mp4"
echo ""
echo "For more information, see README.md"

