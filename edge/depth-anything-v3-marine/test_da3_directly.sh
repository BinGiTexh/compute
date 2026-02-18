#!/bin/bash
echo "Testing proven DA3 approach with NumPy fix..."

docker run --rm --runtime=nvidia --gpus all \
    -v /jetson-ssd:/jetson-ssd \
    v3-marine-simple:latest bash -c "
        echo 'Step 1: Fix NumPy compatibility'
        pip3 install --index-url https://pypi.org/simple/ 'numpy==1.24.3' --force-reinstall --quiet
        
        echo 'Step 2: Test DA3 with fixed dependencies'
        python3 /jetson-ssd/compute/edge/depth-anything-v3-marine/v3_working_pipeline/simple_v3_test_fixed.py
    "
