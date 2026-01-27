#!/usr/bin/env python3
from turtle_depth_processor import TurtleDepthProcessorTRT
import os

print("🐢 TensorRT Depth-Anything-V3 Marine Turtle Analysis")
print("🚀 Jetson AGX Orin Implementation")
print("="*50)

# Get parameters from environment
model_size = os.environ.get('MODEL_SIZE', 'small')
max_frames = int(os.environ.get('MAX_FRAMES', '5'))
skip_frames = int(os.environ.get('SKIP_FRAMES', '600'))

processor = TurtleDepthProcessorTRT(model_size=model_size)

video_path = "/workspace/videos/LORETO_transcto_1_tortuga_sur_FULL.MP4"
output_dir = "/workspace/output/turtle_depth_trt"

result = processor.process_video_robust(video_path, output_dir, max_frames=max_frames, skip_frames=skip_frames)

if result > 0:
    print(f"\n🎉 Analysis completed successfully!")
else:
    print(f"\n❌ Analysis failed")
