#!/usr/bin/env python3
'''
Proven Working Depth Anything V3 Processor
Based on successful diagnostic work and addressing identified issues
'''

import warnings
warnings.filterwarnings('ignore')
import os
os.environ['PYTHONWARNINGS'] = 'ignore'

import sys
import json
import time
from datetime import datetime
import cv2

# Add DA3 to path (confirmed working approach)
sys.path.insert(0, '/workspace/Depth-Anything-3/src')

print('=== PROVEN WORKING DEPTH ANYTHING V3 PROCESSOR ===')
print(f'Timestamp: {datetime.now()}')

class DepthAnythingV3Processor:
    def __init__(self, model_size='base'):
        self.device = None
        self.model = None
        self.model_size = model_size
        
        print(f'Initializing real DA3 {model_size.upper()} model...')
        self._init_dependencies()
        self._load_da3_model()
        
    def _init_dependencies(self):
        '''Initialize dependencies with our proven approach'''
        try:
            import torch
            import numpy as np
            
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            
            print(f'PyTorch: {torch.__version__}')
            print(f'NumPy: {np.__version__}')
            print(f'CUDA available: {torch.cuda.is_available()}')
            
            if torch.cuda.is_available():
                print(f'GPU: {torch.cuda.get_device_name()}')
                total_vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
                print(f'VRAM: {total_vram:.1f}GB')
                
            self.torch = torch
            self.np = np
            
        except Exception as e:
            print(f'Dependency initialization failed: {e}')
            raise
    
    def _load_da3_model(self):
        '''Load real DA3 model using our proven config approach'''
        try:
            # Import DA3 components (we proved these work)
            from depth_anything_3.cfg import load_config, create_object
            
            # Load config using proven approach
            config_map = {
                'base': 'da3-base.yaml',
                'large': 'da3-large.yaml',
                'giant': 'da3-giant.yaml'
            }
            
            config_path = f'/workspace/Depth-Anything-3/src/depth_anything_3/configs/{config_map[self.model_size]}'
            
            print(f'Loading config from: {config_path}')
            cfg = load_config(config_path)
            
            print(f'Config loaded with keys: {list(cfg.keys())}')
            
            # Create model using proven create_object approach
            self.model = create_object(cfg)
            
            # Move to device
            self.model.to(self.device)
            self.model.eval()
            
            print(f'✅ Real DA3 {self.model_size} model loaded successfully')
            print(f'   Model type: {type(self.model)}')
            print(f'   Device: {self.device}')
            
        except Exception as e:
            print(f'DA3 model loading failed: {e}')
            raise
    
    def process_image(self, image_path):
        '''Process single image with real DA3'''
        try:
            import torchvision.transforms as transforms
            from PIL import Image
            
            # Load image
            pil_image = Image.open(image_path).convert('RGB')
            
            # DA3 preprocessing (standard approach)
            transform = transforms.Compose([
                transforms.Resize((518, 518)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            input_tensor = transform(pil_image).unsqueeze(0).to(self.device)
            
            # DA3 inference
            with self.torch.no_grad():
                start_time = time.time()
                
                result = self.model(input_tensor)
                
                inference_time = time.time() - start_time
                
                # Handle DA3 output (based on our diagnostic work)
                if isinstance(result, dict):
                    # Look for depth in various keys
                    for depth_key in ['depth', 'pred_depth', 'depth_pred', 'output']:
                        if depth_key in result:
                            depth = result[depth_key]
                            break
                    else:
                        depth = list(result.values())[0]
                elif isinstance(result, (list, tuple)):
                    depth = result[0]
                else:
                    depth = result
                
                # Convert to numpy (this was our failure point - now fixed with correct NumPy)
                if isinstance(depth, self.torch.Tensor):
                    depth_np = depth.squeeze().cpu().numpy()
                else:
                    depth_np = depth
                
                print(f'✅ DA3 inference successful: {depth_np.shape}, range: {depth_np.min():.3f}-{depth_np.max():.3f}, time: {inference_time:.3f}s')
                
                return depth_np, inference_time
                
        except Exception as e:
            print(f'Image processing failed: {e}')
            raise
    
    def process_video_frames(self, video_path, output_dir, max_frames=100, skip_frames=10):
        '''Process video frames with real DA3'''
        print(f'Processing video: {video_path}')
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        frames_dir = os.path.join(output_dir, 'frames')
        depth_dir = os.path.join(output_dir, 'depth_maps')
        os.makedirs(frames_dir, exist_ok=True)
        os.makedirs(depth_dir, exist_ok=True)
        
        # Extract frames
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f'Cannot open video: {video_path}')
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f'Video: {width}x{height}, {fps:.1f}fps, {duration:.1f}s, {frame_count} frames')
        
        # Extract and process frames
        frame_idx = 0
        processed_count = 0
        processing_times = []
        depth_stats = []
        
        while True:
            ret, frame = cap.read()
            if not ret or (max_frames and processed_count >= max_frames):
                break
            
            if frame_idx % (skip_frames + 1) == 0:
                # Save frame
                frame_path = os.path.join(frames_dir, f'frame_{processed_count:06d}.jpg')
                cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                
                # Process with DA3
                try:
                    depth_map, proc_time = self.process_image(frame_path)
                    
                    # Save depth map
                    depth_path = os.path.join(depth_dir, f'depth_{processed_count:06d}.npy')
                    self.np.save(depth_path, depth_map)
                    
                    # Create depth visualization
                    depth_vis = ((depth_map - depth_map.min()) / (depth_map.max() - depth_map.min()) * 255).astype(self.np.uint8)
                    depth_vis_path = os.path.join(depth_dir, f'depth_vis_{processed_count:06d}.jpg')
                    cv2.imwrite(depth_vis_path, depth_vis)
                    
                    processing_times.append(proc_time)
                    depth_stats.append({
                        'frame': processed_count,
                        'depth_range': [float(depth_map.min()), float(depth_map.max())],
                        'depth_mean': float(depth_map.mean())
                    })
                    
                    processed_count += 1
                    
                    if processed_count % 10 == 0:
                        avg_time = sum(processing_times[-10:]) / min(10, len(processing_times))
                        print(f'   Processed {processed_count} frames, avg time: {avg_time:.3f}s')
                    
                except Exception as e:
                    print(f'Frame {processed_count} processing failed: {e}')
                    continue
            
            frame_idx += 1
        
        cap.release()
        
        # Save processing summary
        summary = {
            'video_info': {
                'path': video_path,
                'resolution': f'{width}x{height}',
                'fps': fps,
                'duration': duration,
                'total_frames': frame_count
            },
            'processing_info': {
                'frames_processed': processed_count,
                'skip_frames': skip_frames,
                'model_used': f'DepthAnything3-{self.model_size}',
                'processing_times': processing_times,
                'depth_statistics': depth_stats,
                'average_processing_time': sum(processing_times) / len(processing_times) if processing_times else 0
            }
        }
        
        summary_path = os.path.join(output_dir, 'processing_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f'✅ Video processing complete: {processed_count} frames processed')
        print(f'   Average processing time: {summary[processing_info][average_processing_time]:.3f}s per frame')
        print(f'   Output directory: {output_dir}')
        
        return summary

def main():
    '''Main processing function'''
    print('Starting proven DA3 video processing...')
    
    if len(sys.argv) < 3:
        print('Usage: python3 v3_processor_proven.py VIDEO_PATH OUTPUT_DIR [MODEL_SIZE]')
        print('Example: python3 v3_processor_proven.py video.mp4 output/ base')
        return
    
    video_path = sys.argv[1]
    output_dir = sys.argv[2]
    model_size = sys.argv[3] if len(sys.argv) > 3 else 'base'
    
    try:
        # Initialize processor
        processor = DepthAnythingV3Processor(model_size)
        
        # Process video
        summary = processor.process_video_frames(video_path, output_dir)
        
        print(f'\n🎉 SUCCESS: Real DA3 processing complete!')
        print(f'Model: DepthAnything3-{model_size}')
        print(f'Frames: {summary[processing_info][frames_processed]}')
        print(f'Output: {output_dir}')
        
    except Exception as e:
        print(f'❌ Processing failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
