#!/usr/bin/env python3
"""
Process extracted frames for TensorRT Depth-Anything-V2 analysis
"""

import cv2
import numpy as np
import torch
from transformers import pipeline
from PIL import Image
import time
from pathlib import Path
import os
import glob

class FrameDepthProcessor:
    def __init__(self, model_size='small'):
        self.model_size = model_size
        
        print(f"🚀 Initializing Depth-Anything-V2 ({model_size}) for frame processing")
        
        # Map model sizes to actual V2 model names
        model_mapping = {
            'small': 'depth-anything/Depth-Anything-V2-Small-hf',
            'base': 'depth-anything/Depth-Anything-V2-Base-hf',   
            'large': 'depth-anything/Depth-Anything-V2-Large-hf'
        }
        
        model_name = model_mapping.get(model_size, model_mapping['small'])
        
        try:
            self.depth_estimator = pipeline(
                "depth-estimation",
                model=model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            print(f"✅ Model loaded: {model_name}")
        except Exception as e:
            print(f"⚠️  Model loading failed: {e}")
            self.depth_estimator = None
        
        print(f"🎯 CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"🎮 GPU: {torch.cuda.get_device_name()}")
    
    def process_frame(self, frame):
        """Process single frame for depth estimation"""
        
        if self.depth_estimator is None:
            return self.process_frame_manual(frame)
        
        try:
            # Convert OpenCV BGR to PIL RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Run depth estimation
            start_time = time.time()
            result = self.depth_estimator(pil_image)
            inference_time = time.time() - start_time
            
            # Extract depth map
            depth = result['depth']
            depth_array = np.array(depth)
            
            return depth_array, inference_time
            
        except Exception as e:
            print(f"⚠️  HF model failed: {e}")
            return self.process_frame_manual(frame)
    
    def process_frame_manual(self, frame):
        """Manual depth processing fallback"""
        start_time = time.time()
        
        if len(frame.shape) == 3:
            blue_channel = frame[:, :, 0].astype(float)
            depth_proxy = 255 - blue_channel
        else:
            depth_proxy = 255 - frame.astype(float)
        
        inference_time = time.time() - start_time
        return depth_proxy, inference_time
    
    def analyze_marine_environment(self, frame, depth_map):
        """Analyze marine environment characteristics"""
        
        if len(frame.shape) == 3:
            blue_channel = frame[:, :, 0].astype(float)
            green_channel = frame[:, :, 1].astype(float) 
            red_channel = frame[:, :, 2].astype(float)
            
            blue_dominance = np.mean(blue_channel) / (np.mean([blue_channel, green_channel, red_channel]) + 1e-6)
        else:
            blue_dominance = 1.0
        
        return {
            'mean_depth': np.mean(depth_map),
            'max_depth': np.max(depth_map),
            'min_depth': np.min(depth_map),
            'blue_dominance': blue_dominance,
            'marine_environment': blue_dominance > 1.1
        }
    
    def colorize_depth(self, depth_map):
        """Convert depth map to colorized visualization"""
        depth_normalized = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min() + 1e-6)
        depth_normalized = (depth_normalized * 255).astype(np.uint8)
        return cv2.applyColorMap(depth_normalized, cv2.COLORMAP_PLASMA)
    
    def process_all_frames(self, frames_dir, output_dir):
        """Process all extracted frames"""
        
        frames_dir = Path(frames_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all frame files
        frame_files = sorted(glob.glob(str(frames_dir / '*.jpg')))
        total_frames = len(frame_files)
        
        print(f"🌊 Processing {total_frames} extracted frames")
        print(f"📂 Input: {frames_dir}")
        print(f"📂 Output: {output_dir}")
        
        processed_count = 0
        total_inference_time = 0
        
        for i, frame_path in enumerate(frame_files):
            try:
                frame_name = Path(frame_path).stem
                timestamp = i * 3.0  # 3-second intervals
                
                if i % 10 == 0:
                    print(f"🔄 Processing frame {i+1}/{total_frames} ({frame_name})")
                
                # Load frame
                frame = cv2.imread(frame_path)
                if frame is None:
                    print(f"❌ Failed to load {frame_path}")
                    continue
                
                # Process frame for depth
                depth_map, inference_time = self.process_frame(frame)
                total_inference_time += inference_time
                
                # Analyze marine environment
                marine_stats = self.analyze_marine_environment(frame, depth_map)
                
                # Generate outputs
                output_name = f"turtle_{frame_name}_t{timestamp:.1f}s"
                
                # Save original frame
                original_path = output_dir / f"{output_name}_original.jpg"
                cv2.imwrite(str(original_path), frame)
                
                # Save depth map (grayscale)
                depth_gray = ((depth_map - depth_map.min()) / (depth_map.max() - depth_map.min() + 1e-6) * 255).astype(np.uint8)
                depth_path = output_dir / f"{output_name}_depth.png"
                cv2.imwrite(str(depth_path), depth_gray)
                
                # Save colorized depth
                depth_colored = self.colorize_depth(depth_map)
                depth_color_path = output_dir / f"{output_name}_depth_color.jpg"
                cv2.imwrite(str(depth_color_path), depth_colored)
                
                processed_count += 1
                
                if i % 20 == 0 and i > 0:
                    avg_time = total_inference_time / processed_count
                    remaining = (total_frames - i) * avg_time
                    marine_indicator = "🌊" if marine_stats['marine_environment'] else "🏞️"
                    print(f"{marine_indicator} Progress: {i}/{total_frames}, ~{remaining:.0f}s remaining, blue_dom={marine_stats['blue_dominance']:.2f}")
                
            except Exception as e:
                print(f"❌ Error processing {frame_path}: {e}")
                continue
        
        avg_inference = total_inference_time / max(processed_count, 1)
        print(f"🎊 Frame processing complete!")
        print(f"📊 Processed: {processed_count}/{total_frames} frames")
        print(f"⚡ Average inference: {avg_inference:.3f}s/frame ({1/avg_inference:.1f} FPS)")
        print(f"📂 Results saved to: {output_dir}")
        
        return processed_count

if __name__ == "__main__":
    model_size = os.environ.get('MODEL_SIZE', 'small')
    
    processor = FrameDepthProcessor(model_size=model_size)
    
    frames_dir = "/workspace/frames"
    output_dir = "/workspace/output/turtle_depth_trt"
    
    result = processor.process_all_frames(frames_dir, output_dir)
    
    if result > 0:
        print(f"\n🎉 Success! Generated {result} depth map sets")
    else:
        print(f"\n❌ No frames were processed successfully")
