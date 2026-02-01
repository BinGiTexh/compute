#!/usr/bin/env python3

"""
Simple Depth Maps to Point Cloud Converter
Uses our existing depth analysis results to generate PLY files
"""

import os
import sys
import numpy as np
import cv2
from PIL import Image
import json
import argparse

def depth_to_pointcloud(depth_map, rgb_image, camera_intrinsics=None):
    """Convert depth map to 3D point cloud"""
    h, w = depth_map.shape
    
    # Default camera intrinsics for marine video (estimated)
    if camera_intrinsics is None:
        fx = fy = min(w, h) * 0.7  # Conservative focal length
        cx, cy = w // 2, h // 2    # Image center
    else:
        fx, fy, cx, cy = camera_intrinsics
    
    # Create coordinate grids
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    
    # Convert depth map to actual depth values (assuming 0-255 range)
    z = depth_map.astype(np.float32) / 255.0 * 10.0  # Scale to ~10m max depth
    
    # Convert to 3D coordinates
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    
    # Stack coordinates
    points = np.stack([x.flatten(), y.flatten(), z.flatten()], axis=1)
    
    # Get RGB colors
    colors = rgb_image.reshape(-1, 3)
    
    # Filter out invalid points
    valid_mask = (z.flatten() > 0.1) & (z.flatten() < 8.0)  # Reasonable depth range
    points = points[valid_mask]
    colors = colors[valid_mask]
    
    return points, colors

def save_ply(points, colors, filename):
    """Save point cloud as PLY file"""
    n_points = len(points)
    
    with open(filename, "w") as f:
        # PLY header
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {n_points}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        
        # Write points
        for i in range(n_points):
            x, y, z = points[i]
            r, g, b = colors[i].astype(int)
            f.write(f"{x:.6f} {y:.6f} {z:.6f} {r} {g} {b}\n")

def process_depth_results(input_dir, output_dir):
    """Convert all depth analysis results to point clouds"""
    depth_dir = os.path.join(input_dir, "turtle_depth_trt")
    
    if not os.path.exists(depth_dir):
        print(f"Error: Depth results not found in {depth_dir}")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all depth files
    depth_files = [f for f in os.listdir(depth_dir) if f.endswith("_depth.png")]
    
    results = []
    for depth_file in sorted(depth_files):
        frame_base = depth_file.replace("_depth.png", "")
        original_file = f"{frame_base}_original.jpg"
        
        depth_path = os.path.join(depth_dir, depth_file)
        original_path = os.path.join(depth_dir, original_file)
        
        if not os.path.exists(original_path):
            print(f"Warning: Original image not found for {depth_file}")
            continue
        
        print(f"Processing: {frame_base}")
        
        # Load depth map and original image
        depth_map = cv2.imread(depth_path, cv2.IMREAD_GRAYSCALE)
        rgb_image = cv2.imread(original_path)
        rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
        
        # Generate point cloud
        points, colors = depth_to_pointcloud(depth_map, rgb_image)
        
        # Save PLY file
        ply_filename = os.path.join(output_dir, f"{frame_base}.ply")
        save_ply(points, colors, ply_filename)
        
        results.append({
            "frame": frame_base,
            "ply_file": ply_filename,
            "num_points": len(points)
        })
        
        print(f"  Generated: {len(points):,} points -> {ply_filename}")
    
    # Save metadata
    metadata = {
        "source_directory": input_dir,
        "output_directory": output_dir,
        "total_frames": len(results),
        "results": results
    }
    
    metadata_file = os.path.join(output_dir, "pointcloud_metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nPoint cloud conversion complete!")
    print(f"Generated {len(results)} PLY files")
    print(f"Metadata: {metadata_file}")

def main():
    parser = argparse.ArgumentParser(description="Convert depth analysis to point clouds")
    parser.add_argument("input_dir", help="Directory with depth analysis results")
    parser.add_argument("--output-dir", default="pointclouds", help="Output directory")
    
    args = parser.parse_args()
    
    output_dir = args.output_dir
    if not output_dir.startswith("/"):
        output_dir = f"{args.input_dir}_{output_dir}"
    
    process_depth_results(args.input_dir, output_dir)

if __name__ == "__main__":
    main()
