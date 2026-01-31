#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple SWANY Depth Processing - No emoji characters for Docker compatibility
"""

import os
import sys
import numpy as np
import cv2
from PIL import Image
import torch
from transformers import pipeline
import json
from datetime import datetime
import argparse

class SwanyDepthProcessor:
    def __init__(self):
        print("Initializing Depth-Anything-V2 model...")
        self.depth_estimator = pipeline(
            "depth-estimation",
            model="depth-anything/Depth-Anything-V2-Base-hf",
            torch_dtype=torch.float16,
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        print("Model loaded successfully")
        
    def process_image(self, image_path, output_prefix):
        """Process single image for depth estimation"""
        print(f"Processing: {image_path}")
        
        # Load image
        image = Image.open(image_path).convert("RGB")
        
        # Marine environment detection (blue channel dominance)
        img_array = np.array(image)
        blue_mean = np.mean(img_array[:, :, 2])
        is_marine = blue_mean > 100
        
        # Run depth estimation
        try:
            depth_result = self.depth_estimator(image)
            depth_map = depth_result["depth"]
            
            # Convert to numpy array
            depth_array = np.array(depth_map)
            
            # Save original image
            original_path = f"{output_prefix}_original.jpg"
            image.save(original_path)
            
            # Save raw depth data
            raw_depth_path = f"{output_prefix}_depth.npy"
            np.save(raw_depth_path, depth_array)
            
            # Create colorized depth map
            depth_normalized = ((depth_array - depth_array.min()) / 
                              (depth_array.max() - depth_array.min()) * 255).astype(np.uint8)
            depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_PLASMA)
            colored_path = f"{output_prefix}_depth_color.jpg"
            cv2.imwrite(colored_path, depth_colored)
            
            return {
                "frame_name": os.path.basename(image_path),
                "is_marine": is_marine,
                "original_path": original_path,
                "raw_depth_path": raw_depth_path,
                "colored_path": colored_path,
                "depth_stats": {
                    "min": float(depth_array.min()),
                    "max": float(depth_array.max()),
                    "mean": float(depth_array.mean())
                }
            }
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="SWANY Depth Processing")
    parser.add_argument("--input_dir", required=True, help="Input frames directory")
    parser.add_argument("--output_dir", required=True, help="Output directory")
    parser.add_argument("--max_frames", type=int, default=10, help="Max frames to process")
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = SwanyDepthProcessor()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get frame files
    frame_files = sorted([f for f in os.listdir(args.input_dir) if f.endswith(.jpg)])
    
    print(f"Found {len(frame_files)} frames, processing first {args.max_frames}")
    
    results = []
    for i, frame_file in enumerate(frame_files[:args.max_frames]):
        frame_path = os.path.join(args.input_dir, frame_file)
        output_prefix = os.path.join(args.output_dir, f"swany_{frame_file.replace(.jpg, )}")
        
        result = processor.process_image(frame_path, output_prefix)
        if result:
            results.append(result)
            print(f"Completed {i+1}/{args.max_frames}: {frame_file}")
        else:
            print(f"Failed {i+1}/{args.max_frames}: {frame_file}")
    
    # Save processing metadata
    metadata = {
        "video_source": "TEST_SWANY.mp4",
        "processing_date": datetime.now().isoformat(),
        "total_processed": len(results),
        "results": results
    }
    
    metadata_path = os.path.join(args.output_dir, "processing_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Processing complete! Processed {len(results)} frames")
    print(f"Results saved to: {args.output_dir}")
    print(f"Metadata: {metadata_path}")

if __name__ == "__main__":
    main()
