#!/usr/bin/env python3
import sys
import os
import torch
import numpy as np
from PIL import Image
import cv2

sys.path.insert(0, '/workspace/Depth-Anything-3/src')

print('=== SIMPLE V3 PROCESSOR ===')
print(f'Python: {sys.version_info.major}.{sys.version_info.minor}')
print(f'PyTorch: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')

if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name()}')

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
