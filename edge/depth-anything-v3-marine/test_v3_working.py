#!/usr/bin/env python3
'''
Test script for proven DA3 pipeline
Validates all components before processing real videos
'''

import warnings
warnings.filterwarnings('ignore')
import os
os.environ['PYTHONWARNINGS'] = 'ignore'

import sys
sys.path.insert(0, '/workspace/Depth-Anything-3/src')

def test_dependencies():
    '''Test that all dependencies work'''
    print('=== Testing Dependencies ===')
    
    try:
        import torch
        import numpy as np
        print(f'✅ PyTorch {torch.__version__}')
        print(f'✅ NumPy {np.__version__}')
        print(f'✅ CUDA available: {torch.cuda.is_available()}')
        
        # Test tensor conversion (this was our main failure point)
        test_tensor = torch.randn(2, 2)
        test_array = test_tensor.cpu().numpy()
        print(f'✅ Tensor conversion works: {test_array.shape}')
        
        return True
    except Exception as e:
        print(f'❌ Dependency test failed: {e}')
        return False

def test_da3_imports():
    '''Test DA3 imports'''
    print('\n=== Testing DA3 Imports ===')
    
    try:
        from depth_anything_3.cfg import load_config, create_object
        print('✅ DA3 config functions imported')
        
        # Test config loading
        config_path = '/workspace/Depth-Anything-3/src/depth_anything_3/configs/da3-base.yaml'
        cfg = load_config(config_path)
        print(f'✅ DA3 config loaded: {list(cfg.keys())}')
        
        return True
    except Exception as e:
        print(f'❌ DA3 import test failed: {e}')
        return False

def test_da3_model():
    '''Test DA3 model creation'''
    print('\n=== Testing DA3 Model Creation ===')
    
    try:
        from depth_anything_3.cfg import load_config, create_object
        import torch
        
        config_path = '/workspace/Depth-Anything-3/src/depth_anything_3/configs/da3-base.yaml'
        cfg = load_config(config_path)
        
        model = create_object(cfg)
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model.to(device)
        model.eval()
        
        print(f'✅ DA3 model created: {type(model)}')
        print(f'✅ Model on device: {device}')
        
        return True, model, device
    except Exception as e:
        print(f'❌ DA3 model test failed: {e}')
        import traceback
        traceback.print_exc()
        return False, None, None

def test_inference():
    '''Test DA3 inference'''
    print('\n=== Testing DA3 Inference ===')
    
    success, model, device = test_da3_model()
    if not success:
        return False
    
    try:
        import torch
        import torchvision.transforms as transforms
        from PIL import Image
        import numpy as np
        
        # Create test image
        test_image = Image.new('RGB', (640, 480), color='blue')
        
        transform = transforms.Compose([
            transforms.Resize((518, 518)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform(test_image).unsqueeze(0).to(device)
        
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
        
        # Convert to numpy (critical test)
        depth_np = depth.squeeze().cpu().numpy()
        
        print(f'✅ DA3 inference successful')
        print(f'   Input shape: {input_tensor.shape}')
        print(f'   Output shape: {depth_np.shape}')
        print(f'   Depth range: {depth_np.min():.3f} to {depth_np.max():.3f}')
        
        return True
    except Exception as e:
        print(f'❌ Inference test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    print('🧪 TESTING PROVEN DA3 PIPELINE')
    print('=' * 40)
    
    # Run all tests
    deps_ok = test_dependencies()
    imports_ok = test_da3_imports()
    inference_ok = test_inference()
    
    print('\n' + '=' * 40)
    print('📊 TEST RESULTS')
    print(f'Dependencies: {✅ PASS if deps_ok else ❌ FAIL}')
    print(f'DA3 Imports: {✅ PASS if imports_ok else ❌ FAIL}')
    print(f'DA3 Inference: {✅ PASS if inference_ok else ❌ FAIL}')
    
    if all([deps_ok, imports_ok, inference_ok]):
        print('\n🎉 ALL TESTS PASSED - PROVEN DA3 PIPELINE READY!')
        return 0
    else:
        print('\n❌ Some tests failed - pipeline needs fixes')
        return 1

if __name__ == '__main__':
    sys.exit(main())
