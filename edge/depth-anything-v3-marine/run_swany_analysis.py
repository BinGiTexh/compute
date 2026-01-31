#!/usr/bin/env python3
from turtle_depth_processor import TurtleDepthProcessorTRT
import os

print("SWANY TensorRT Depth-Anything-V2 Analysis")
print("Jetson AGX Orin Implementation")
print("="*50)

processor = TurtleDepthProcessorTRT(model_size="small")

video_path = "/workspace/videos/TEST_SWANY.mp4"
output_dir = "/workspace/output/swany_depth_trt"

result = processor.process_video_robust(video_path, output_dir, max_frames=20, skip_frames=90)

if result > 0:
    print(f"Analysis completed successfully! Processed {result} frames")
else:
    print("Analysis failed")
