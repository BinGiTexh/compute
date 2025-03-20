## Compiling a list of sources of best practices when working with Jetsons
https://docs.ultralytics.com/guides/nvidia-jetson/#best-practices-when-using-nvidia-jetson

## Devices will be showcased as Internal github runners that can be invoked upon demand closer to the codebase


## Requirements
Jetson Super Nano 8GB - dusty containers image https://www.jetson-ai-lab.com/vit/tutorial_nanoowl.html

## Download container
jetson-containers run --workdir /opt/nanoowl $(autotag nanoowl)

## Copy videos and script  to container
docker cp GH011294.MP4  jetson_container_20250320_125557:/opt/nanoowl
nanoowl_inference.py


## Example usage
python3 nanoowl_inference.py data/owl_image_encoder_patch32.engine GH011294.MP4  output.mp4  --prompt "Find all fish in the scene" --resize "640x480"


## Models/ Scripts

Nanoowl_inference.py

This file is a Python script for processing video files with NanoOWL, which appears to be a computer vision model from NVIDIA for detecting objects in images.
The script specifically:

Takes a video file as input
Processes each frame using the NanoOWL object detection model
Draws bounding boxes or other visualizations of the detected objects on each frame
Saves the annotated video to an output file


