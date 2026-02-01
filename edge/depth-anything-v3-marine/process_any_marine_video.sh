#!/bin/bash

# Universal Marine Video Depth Analysis
# One-command processing for any marine video

VIDEO_PATH="$1"

if [ -z "$VIDEO_PATH" ]; then
    echo "Usage: $0 [VIDEO_PATH]"
    echo "Example: $0 my_marine_video.mp4"
    exit 1
fi

if [ ! -f "$VIDEO_PATH" ]; then
    echo "Error: Video not found: $VIDEO_PATH"
    exit 1
fi

# Get video name for output directory
VIDEO_NAME=$(basename "$VIDEO_PATH" | sed "s/\.[^.]*$//")
OUTPUT_DIR="${VIDEO_NAME}_depth_output"

echo "Processing: $VIDEO_PATH"
echo "Output: $OUTPUT_DIR"
echo ""

# Run proven depth analysis
docker run --rm --runtime=nvidia --gpus all \
    -v "$(realpath "$VIDEO_PATH")":/workspace/videos/LORETO_transcto_1_tortuga_sur_FULL.MP4:ro \
    -v "$(realpath .)"/$OUTPUT_DIR:/workspace/output \
    -e MODEL_SIZE="small" \
    -e MAX_FRAMES="20" \
    -e SKIP_FRAMES="90" \
    jetson-depth-anything-v3-trt:latest

echo ""
echo "Complete! Results in: $OUTPUT_DIR/"
find "$OUTPUT_DIR" -name "*.jpg" -o -name "*.png" | wc -l | xargs echo "Output files:"
