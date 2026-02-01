#!/usr/bin/env python3

import os
import numpy as np
import cv2

def depth_to_pointcloud_simple(depth_map, rgb_image):
    """Simple depth to point cloud conversion"""
    h, w = depth_map.shape
    
    # Camera parameters (estimated for marine video)
    fx = fy = min(w, h) * 0.7  # focal length
    cx, cy = w // 2, h // 2    # principal point
    
    # Downsample for faster processing (every 4th pixel)
    step = 4
    depth_small = depth_map[::step, ::step]
    rgb_small = rgb_image[::step, ::step]
    h_small, w_small = depth_small.shape
    
    # Create coordinate grids
    u, v = np.meshgrid(np.arange(w_small), np.arange(h_small))
    u = u * step  # Scale back to original coordinates
    v = v * step
    
    # Convert depth (0-255) to meters (0-8m)
    z = depth_small.astype(np.float32) / 255.0 * 8.0
    
    # 3D coordinates
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    
    # Stack points
    points = np.stack([x.flatten(), y.flatten(), z.flatten()], axis=1)
    colors = rgb_small.reshape(-1, 3)
    
    # Filter valid points
    valid = (z.flatten() > 0.2) & (z.flatten() < 6.0)
    points = points[valid]
    colors = colors[valid]
    
    return points, colors

def save_ply_simple(points, colors, filename):
    """Save PLY file"""
    print(f"Saving {len(points)} points to {filename}")
    
    with open(filename, "w") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(points)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        
        for i, (point, color) in enumerate(zip(points, colors)):
            x, y, z = point
            r, g, b = color.astype(int)
            f.write(f"{x:.3f} {y:.3f} {z:.3f} {r} {g} {b}\n")

# Test with first frame
print("Testing point cloud conversion...")

depth_file = "./output/turtle_depth_trt/turtle_frame_000001_t0.0s_depth.png"
original_file = "./output/turtle_depth_trt/turtle_frame_000001_t0.0s_original.jpg"

# Load images
depth_map = cv2.imread(depth_file, cv2.IMREAD_GRAYSCALE)
rgb_image = cv2.imread(original_file)
rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)

print(f"Processing: {depth_map.shape} depth map")

# Generate point cloud
points, colors = depth_to_pointcloud_simple(depth_map, rgb_image)

# Save result
os.makedirs("test_pointcloud", exist_ok=True)
save_ply_simple(points, colors, "test_pointcloud/turtle_frame_001.ply")

print(f"Generated point cloud with {len(points):,} points")
print("Test complete! Check test_pointcloud/turtle_frame_001.ply")
