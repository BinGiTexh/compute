#!/usr/bin/env python3

import os
import numpy as np
import cv2
import glob

def depth_to_pointcloud_simple(depth_map, rgb_image):
    """Simple depth to point cloud conversion"""
    h, w = depth_map.shape
    
    # Camera parameters
    fx = fy = min(w, h) * 0.7
    cx, cy = w // 2, h // 2
    
    # Downsample for performance
    step = 4
    depth_small = depth_map[::step, ::step]
    rgb_small = rgb_image[::step, ::step]
    h_small, w_small = depth_small.shape
    
    u, v = np.meshgrid(np.arange(w_small), np.arange(h_small))
    u, v = u * step, v * step
    
    z = depth_small.astype(np.float32) / 255.0 * 8.0
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    
    points = np.stack([x.flatten(), y.flatten(), z.flatten()], axis=1)
    colors = rgb_small.reshape(-1, 3)
    
    valid = (z.flatten() > 0.2) & (z.flatten() < 6.0)
    return points[valid], colors[valid]

def save_ply_simple(points, colors, filename):
    """Save PLY file"""
    with open(filename, "w") as f:
        f.write(f"ply\nformat ascii 1.0\nelement vertex {len(points)}\n")
        f.write("property float x\nproperty float y\nproperty float z\n")
        f.write("property uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n")
        
        for point, color in zip(points, colors):
            x, y, z = point
            r, g, b = color.astype(int)
            f.write(f"{x:.3f} {y:.3f} {z:.3f} {r} {g} {b}\n")

# Process first 10 frames
print("Processing first 10 turtle frames...")
os.makedirs("turtle_pointclouds", exist_ok=True)

depth_files = sorted(glob.glob("./output/turtle_depth_trt/*_depth.png"))[:10]

for i, depth_file in enumerate(depth_files):
    frame_base = os.path.basename(depth_file).replace("_depth.png", "")
    original_file = depth_file.replace("_depth.png", "_original.jpg")
    
    if not os.path.exists(original_file):
        print(f"Skipping {frame_base} - no original image")
        continue
    
    print(f"Processing {i+1}/10: {frame_base}")
    
    # Load images
    depth_map = cv2.imread(depth_file, cv2.IMREAD_GRAYSCALE)
    rgb_image = cv2.imread(original_file)
    rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
    
    # Generate point cloud
    points, colors = depth_to_pointcloud_simple(depth_map, rgb_image)
    
    # Save PLY
    ply_file = f"turtle_pointclouds/{frame_base}.ply"
    save_ply_simple(points, colors, ply_file)
    
    print(f"  -> {len(points):,} points saved to {ply_file}")

print("\nBatch processing complete!")
print("Check turtle_pointclouds/ directory for PLY files")
