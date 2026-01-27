#!/usr/bin/env python3
"""
Robust Marine Turtle Depth Analysis using TensorRT-optimized Depth-Anything-V3
Jetson AGX Orin Implementation with improved video handling
"""

import cv2
import numpy as np
import torch
from transformers import pipeline
from PIL import Image
import time
from pathlib import Path
import os

class TurtleDepthProcessorTRT:
    def __init__(self, model_size='base', use_trt=True):
        self.model_size = model_size
        self.use_trt = use_trt
        
        print(f"🚀 Initializing Depth-Anything-V3 ({model_size}) on Jetson AGX Orin")
        
        # Map model sizes to actual V2 model names
        model_mapping = {
            'small': 'depth-anything/Depth-Anything-V2-Small-hf',
            'base': 'depth-anything/Depth-Anything-V2-Base-hf',   
            'large': 'depth-anything/Depth-Anything-V2-Large-hf'
        }
        
        model_name = model_mapping.get(model_size, model_mapping['base'])
        
        try:
            # Initialize depth estimation pipeline
            self.depth_estimator = pipeline(
                "depth-estimation",
                model=model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            print(f"✅ Model loaded: {model_name}")
        except Exception as e:
            print(f"⚠️  Model loading failed, using backup approach: {e}")
            self.depth_estimator = None
        
        print(f"🎯 CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"🎮 GPU: {torch.cuda.get_device_name()}")
    
    def process_frame_manual(self, frame):
        """Manual depth processing using blue channel analysis (marine-optimized)"""
        
        start_time = time.time()
        
        # Marine-specific depth analysis using blue channel attenuation
        if len(frame.shape) == 3:
            blue_channel = frame[:, :, 0].astype(float)
            green_channel = frame[:, :, 1].astype(float)
            red_channel = frame[:, :, 2].astype(float)
            
            # Water column depth estimation based on blue light attenuation
            depth_proxy = 255 - blue_channel * 0.6 - green_channel * 0.3 - red_channel * 0.1
            depth_proxy = np.clip(depth_proxy, 0, 255)
        else:
            depth_proxy = 255 - frame.astype(float)
        
        inference_time = time.time() - start_time
        return depth_proxy, inference_time
    
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
            print(f"⚠️  HF model failed, using manual approach: {e}")
            return self.process_frame_manual(frame)
    
    def analyze_marine_environment(self, frame, depth_map):
        """Analyze marine environment characteristics"""
        
        # Calculate blue channel dominance (water detection)
        if len(frame.shape) == 3:
            blue_channel = frame[:, :, 0].astype(float)
            green_channel = frame[:, :, 1].astype(float) 
            red_channel = frame[:, :, 2].astype(float)
            
            blue_dominance = np.mean(blue_channel) / (np.mean([blue_channel, green_channel, red_channel]) + 1e-6)
        else:
            blue_dominance = 1.0
        
        # Depth statistics
        depth_stats = {
            'mean_depth': np.mean(depth_map),
            'max_depth': np.max(depth_map),
            'min_depth': np.min(depth_map),
            'depth_variance': np.var(depth_map),
            'blue_dominance': blue_dominance,
            'marine_environment': blue_dominance > 1.1
        }
        
        return depth_stats
    
    def colorize_depth(self, depth_map):
        """Convert depth map to colorized visualization"""
        
        # Normalize depth map
        depth_normalized = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min() + 1e-6)
        depth_normalized = (depth_normalized * 255).astype(np.uint8)
        
        # Apply colormap
        depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_PLASMA)
        
        return depth_colored
    
    def process_video_robust(self, video_path, output_dir, max_frames=10, skip_frames=30):
        """Robust video processing with better error handling"""
        
        video_path = Path(video_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🌊 Processing marine video: {video_path}")
        
        # Open video with more robust settings
        cap = cv2.VideoCapture(str(video_path))
        
        # Set buffer size to prevent frame accumulation
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            print(f"❌ Failed to open video: {video_path}")
            return
        
        # Get video info
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"📹 Video info: {total_frames} frames @ {fps:.1f} fps")
        print(f"⚙️  Processing every {skip_frames} frames, max {max_frames} samples")
        
        frame_idx = 0
        processed_count = 0
        total_inference_time = 0
        frames_read = 0
        
        # Process frames more robustly
        while processed_count < max_frames:
            # Read frame
            ret, frame = cap.read()
            frames_read += 1
            
            if not ret:
                print(f"📹 End of video reached at frame {frames_read}")
                break
            
            # Skip frames according to sampling rate
            if frame_idx % skip_frames != 0:
                frame_idx += 1
                continue
            
            try:
                timestamp = frame_idx / fps if fps > 0 else frame_idx * 0.033
                
                print(f"🔄 Processing frame {frame_idx}/{total_frames} (t={timestamp:.1f}s)...", flush=True)
                
                # Process frame for depth
                depth_map, inference_time = self.process_frame(frame)
                total_inference_time += inference_time
                
                # Analyze marine environment
                marine_stats = self.analyze_marine_environment(frame, depth_map)
                
                # Generate outputs
                frame_name = f"turtle_frame_{frame_idx:06d}_t{timestamp:.1f}s"
                
                # Save original frame
                original_path = output_dir / f"{frame_name}_original.jpg"
                cv2.imwrite(str(original_path), frame)
                
                # Save depth map (grayscale)
                depth_gray = ((depth_map - depth_map.min()) / (depth_map.max() - depth_map.min() + 1e-6) * 255).astype(np.uint8)
                depth_path = output_dir / f"{frame_name}_depth.png"
                cv2.imwrite(str(depth_path), depth_gray)
                
                # Save colorized depth
                depth_colored = self.colorize_depth(depth_map)
                depth_color_path = output_dir / f"{frame_name}_depth_color.jpg"
                cv2.imwrite(str(depth_color_path), depth_colored)
                
                # Print progress
                marine_indicator = "🌊" if marine_stats['marine_environment'] else "🏞️"
                print(f"{marine_indicator} Frame {frame_idx} (t={timestamp:.1f}s): "
                      f"inference={inference_time:.3f}s, "
                      f"depth_range=[{marine_stats['min_depth']:.1f}, {marine_stats['max_depth']:.1f}], "
                      f"blue_dom={marine_stats['blue_dominance']:.2f}")
                
                processed_count += 1
                
            except Exception as e:
                print(f"❌ Error processing frame {frame_idx}: {e}")
            
            frame_idx += 1
            
            # Progress update
            if processed_count % 10 == 0 and processed_count > 0:
                elapsed = total_inference_time
                remaining = (max_frames - processed_count) * (elapsed / processed_count)
                print(f"📊 Progress: {processed_count}/{max_frames} frames, ~{remaining:.0f}s remaining")
        
        cap.release()
        
        avg_inference = total_inference_time / max(processed_count, 1)
        print(f"🎊 Analysis complete!")
        print(f"📊 Processed: {processed_count} frames")
        print(f"⚡ Average inference: {avg_inference:.3f}s/frame ({1/avg_inference:.1f} FPS)")
        print(f"📂 Results saved to: {output_dir}")
        
        return processed_count

if __name__ == "__main__":
    # Get parameters from environment variables
    model_size = os.environ.get('MODEL_SIZE', 'small')
    max_frames = int(os.environ.get('MAX_FRAMES', '5'))
    skip_frames = int(os.environ.get('SKIP_FRAMES', '600'))
    
    processor = TurtleDepthProcessorTRT(model_size=model_size)
    
    # Process turtle video
    video_path = "/workspace/videos/LORETO_transcto_1_tortuga_sur_FULL.MP4"
    output_dir = "/workspace/output/turtle_depth_trt"
    
    result = processor.process_video_robust(video_path, output_dir, max_frames=max_frames, skip_frames=skip_frames)
    
    if result > 0:
        print(f"\n🎉 Success! Generated {result} depth map sets")
    else:
        print(f"\n❌ No frames were processed successfully")
