#!/bin/bash

# Get the container tag from the first argument or use the latest tag
CONTAINER_TAG=${1:-$(docker images --format "{{.Repository}}" | grep boltz | head -n 1)}

if [ -z "$CONTAINER_TAG" ]; then
  echo "Error: No Boltz container found. Please build the container first or specify the tag."
  exit 1
fi

echo "Testing Boltz container: $CONTAINER_TAG"
echo "=================================="

# Create required directories if they don't exist
mkdir -p data models examples

# Run the container with the test script
echo "Starting container for testing..."
docker run --gpus all -it --rm \
  -v $(pwd)/examples:/workspace/examples \
  -v $(pwd)/data:/workspace/data \
  -v $(pwd)/models:/workspace/models \
  $CONTAINER_TAG python /workspace/examples/test_boltz.py

# Test a simple prediction if test script passes
echo ""
echo "To run a simple prediction test, use:"
echo "docker run --gpus all -it --rm \\"
echo "  -v $(pwd)/examples:/workspace/examples \\"
echo "  -v $(pwd)/data:/workspace/data \\"
echo "  -v $(pwd)/models:/workspace/models \\"
echo "  $CONTAINER_TAG boltz predict /workspace/examples/simple_input.yaml --use_msa_server"

