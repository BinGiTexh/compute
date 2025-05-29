#!/usr/bin/env python3

import cv2
import numpy as np
import os
from pathlib import Path

def create_test_video(output_path: str, duration: int = 10, fps: int = 30, width: int = 1280, height: int = 720):
    """Create a test video with moving objects for testing the pipeline."""
    
    # Create output directory if it doesn't exist
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Create moving objects
    total_frames = duration * fps
    
    for frame_num in range(total_frames):
        # Create blue background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :] = (128, 64, 0)  # BGR format
        
        # Add moving "diver" (white rectangle)
        x = int((frame_num / total_frames) * width)
        y = int(height/2 + np.sin(frame_num/20) * 100)
        cv2.rectangle(frame, (x, y), (x+100, y+50), (255, 255, 255), -1)
        
        # Add timestamp
        cv2.putText(frame, f"Frame: {frame_num}", (10, 30),
                  cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    print(f"Created test video: {output_path}")

if __name__ == "__main__":
    output_path = "test_videos/test_diver_video.mp4"
    create_test_video(output_path)
