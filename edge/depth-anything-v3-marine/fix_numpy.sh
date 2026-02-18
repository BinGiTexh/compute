#!/bin/bash
# Quick fix for NumPy compatibility issue in existing container
echo "Fixing NumPy compatibility for real DA3..."

# Run container with NumPy fix
docker run --rm --runtime=nvidia --gpus all \
    -v /jetson-ssd:/jetson-ssd \
    v3-marine-simple:latest bash -c "
        echo 'Downgrading NumPy for PyTorch compatibility...'
        pip3 install 'numpy==1.24.3' --force-reinstall --quiet
        
        echo 'Testing fixed DA3...'
        python3 /jetson-ssd/compute/edge/depth-anything-v3-marine/v3_working_pipeline/simple_v3_test.py
    "
