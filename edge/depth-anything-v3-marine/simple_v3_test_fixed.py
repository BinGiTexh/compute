#!/usr/bin/env python3
import warnings
warnings.filterwarnings('ignore')
import os
os.environ['PYTHONWARNINGS'] = 'ignore'
import sys
sys.path.insert(0, '/workspace/Depth-Anything-3/src')

print('=== Testing FIXED DA3 Pipeline ===')

# Test 1: Basic dependencies
try:
    import torch
    import numpy as np
    print(f'Dependencies OK: PyTorch {torch.__version__}, NumPy {np.__version__}')
    
    # Test tensor conversion (our critical test)
    test_tensor = torch.randn(2, 2)
    test_array = test_tensor.cpu().numpy()
    print(f'Tensor conversion OK: {test_array.shape}')
    
except Exception as e:
    print(f'Dependencies FAILED: {e}')
    sys.exit(1)

# Test 2: DA3 imports
try:
    from depth_anything_3.cfg import load_config, create_object
    print('DA3 imports OK')
except Exception as e:
    print(f'DA3 imports FAILED: {e}')
    sys.exit(1)

# Test 3: DA3 model loading
try:
    config_path = '/workspace/Depth-Anything-3/src/depth_anything_3/configs/da3-base.yaml'
    cfg = load_config(config_path)
    model = create_object(cfg)
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    model.eval()
    
    print(f'DA3 model OK: {type(model)} on {device}')
except Exception as e:
    print(f'DA3 model FAILED: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: DA3 inference with CORRECT input format
try:
    import torchvision.transforms as transforms
    from PIL import Image
    
    # Create test images (DA3 may expect batch of images)
    test_image1 = Image.new('RGB', (640, 480), color='blue')
    test_image2 = Image.new('RGB', (640, 480), color='red')
    
    transform = transforms.Compose([
        transforms.Resize((518, 518)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Try different input formats for DA3
    input_formats = [
        # Standard single image (what failed)
        transform(test_image1).unsqueeze(0).to(device),
        
        # Batch of images (may be what DA3 expects)
        torch.stack([transform(test_image1), transform(test_image2)]).to(device),
        
        # Single image with extra dimension
        transform(test_image1).unsqueeze(0).unsqueeze(0).to(device),
    ]
    
    for i, input_tensor in enumerate(input_formats):
        try:
            print(f'Trying input format {i+1}: shape {input_tensor.shape}')
            
            with torch.no_grad():
                result = model(input_tensor)
            
            # Handle result
            if isinstance(result, dict):
                for key in ['depth', 'pred_depth', 'output']:
                    if key in result:
                        depth = result[key]
                        break
                else:
                    depth = list(result.values())[0]
            else:
                depth = result
            
            # Convert to numpy (CRITICAL TEST - now fixed!)
            if isinstance(depth, (list, tuple)):
                depth_np = depth[0].squeeze().cpu().numpy()
            else:
                depth_np = depth.squeeze().cpu().numpy()
            
            print(f'DA3 inference SUCCESS with format {i+1}!')
            print(f'   Input: {input_tensor.shape}')  
            print(f'   Output: {depth_np.shape}, range {depth_np.min():.3f}-{depth_np.max():.3f}')
            break
            
        except Exception as e:
            print(f'   Format {i+1} failed: {e}')
            if i == len(input_formats) - 1:  # Last attempt
                raise e
    
except Exception as e:
    print(f'DA3 inference FAILED: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\nSUCCESS: All DA3 tests passed!')
print('BREAKTHROUGH: Real Depth Anything V3 working with NumPy fix!')
print('Ready for ESPERANZA video processing')
