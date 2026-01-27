#!/bin/bash

# TensorRT Depth-Anything-V3 Marine Turtle Analysis Runner
# Isolated Docker environment for Jetson AGX Orin

set -e

echo "🐢 Starting TensorRT Depth-Anything-V3 Analysis"
echo "🚀 Jetson AGX Orin - Isolated Docker Environment"
echo "="*60

# Configuration
MODEL_SIZE=${MODEL_SIZE:-small}
MAX_FRAMES=${MAX_FRAMES:-5}
SKIP_FRAMES=${SKIP_FRAMES:-600}
VIDEO_PATH="/home/mza-bingi/LORETO_transcto_1_tortuga_sur_FULL.MP4"
OUTPUT_DIR="/jetson-ssd/depth-anything-v3-trt/output"

echo "📋 Configuration:"
echo "   Model Size: $MODEL_SIZE"
echo "   Max Frames: $MAX_FRAMES"
echo "   Skip Frames: $SKIP_FRAMES"
echo "   Video Path: $VIDEO_PATH"
echo "   Output Dir: $OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if video exists
if [[ ! -f "$VIDEO_PATH" ]]; then
    echo "❌ Error: Video file not found: $VIDEO_PATH"
    exit 1
fi

echo ""
echo "🚀 Launching Docker container with GPU support..."

# Run the Docker container with NVIDIA runtime
docker run --rm \
    --runtime=nvidia \
    --gpus all \
    -v "$VIDEO_PATH":/workspace/videos/LORETO_transcto_1_tortuga_sur_FULL.MP4:ro \
    -v "$OUTPUT_DIR":/workspace/output \
    -e MODEL_SIZE="$MODEL_SIZE" \
    -e MAX_FRAMES="$MAX_FRAMES" \
    -e SKIP_FRAMES="$SKIP_FRAMES" \
    jetson-depth-anything-v3-trt:latest

echo ""
echo "✅ Analysis completed!"
echo "📂 Results available in: $OUTPUT_DIR"
ls -la "$OUTPUT_DIR"
