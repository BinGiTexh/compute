#!/usr/bin/env python3
import sys
import os
import torch
import numpy as np
from PIL import Image
import cv2

sys.path.insert(0, '/workspace/Depth-Anything-3/src')

# Configuration - Model size selection
MODEL_SIZE = os.environ.get('V3_MODEL_SIZE', 'base')  # base, large, or giant

MODEL_MAP = {
    'base': 'depth-anything/da3-base',
    'large': 'depth-anything/da3-large', 
    'giant': 'depth-anything/da3-giant'
}

print(f'=== V3 PROCESSOR ({MODEL_SIZE.upper()}) ===')
print(f'Python: {sys.version_info.major}.{sys.version_info.minor}')
print(f'PyTorch: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')

if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name()}')
    total_vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f'VRAM Available: {total_vram:.1f}GB')

print(f'Selected Model: {MODEL_MAP.get(MODEL_SIZE, MODEL_MAP[base])}')

# Test V3 import
try:
    import depth_anything_3
    print('✅ V3 module imported')
    
    from depth_anything_3.api import DepthAnything3
    print('✅ V3 API ready')
    print('🎉 V3 PROCESSOR READY!')
    
except Exception as e:
    print(f'V3 import issue: {e}')
    print('Will attempt basic functionality')

print('V3 Processor initialized!')
