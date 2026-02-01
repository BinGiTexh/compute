#!/bin/bash

# Universal Marine Video Depth Analysis Processor  
# Uses proven jetson-depth-anything-v3-trt container
# Works with any marine video - no modifications needed

set -e

# Usage function
usage() {
    echo "Usage: $0 [VIDEO_PATH] [OPTIONS]"
    echo ""
    echo "Required:"
    echo "  VIDEO_PATH    Path to marine video file"
    echo ""
    echo "Options:"
    echo "  --max-frames N     Max frames to process (default: 20)"
    echo "  --skip-frames N    Frame skip interval (default: 90)"
    echo "  --model-size SIZE  Model size: small|base|large (default: small)"
    echo "  --output-dir DIR   Output directory (default: ./[video_name]_output)"
    echo ""
    echo "Examples:"
    echo "  $0 my_marine_video.mp4"
    echo "  $0 coral_survey.mp4 --max-frames 30 --skip-frames 60"
    echo "  $0 /path/to/video.mp4 --output-dir /custom/output"
}

# Default parameters
MAX_FRAMES=20
SKIP_FRAMES=90
MODEL_SIZE="small"
OUTPUT_DIR=""

# Parse arguments
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

VIDEO_PATH="$1"
shift

while [[ $# -gt 0 ]]; do
    case $1 in
        --max-frames)
            MAX_FRAMES="$2"
            shift 2
            ;;
        --skip-frames)
            SKIP_FRAMES="$2" 
            shift 2
            ;;
        --model-size)
            MODEL_SIZE="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate video file
if [[ ! -f "$VIDEO_PATH" ]]; then
    echo "Error: Video file not found: $VIDEO_PATH"
    exit 1
fi

# Set default output directory if not provided
if [[ -z "$OUTPUT_DIR" ]]; then
    VIDEO_NAME=$(basename "$VIDEO_PATH" | sed 's/\.[^.]*$//')
    OUTPUT_DIR="${VIDEO_NAME}_depth_output"
fi

# Get absolute paths
VIDEO_PATH=$(realpath "$VIDEO_PATH")
OUTPUT_DIR=$(realpath "$OUTPUT_DIR")

echo "Universal Marine Video Depth Analysis"
echo "===================================="
echo "Video: $(basename "$VIDEO_PATH")"
echo "Output: $OUTPUT_DIR" 
echo "Model: $MODEL_SIZE"
echo "Max Frames: $MAX_FRAMES"
echo "Skip Frames: $SKIP_FRAMES"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Starting depth analysis..."

# Run the proven container
docker run --rm --runtime=nvidia --gpus all \
    -v "$VIDEO_PATH":/workspace/videos/LORETO_transcto_1_tortuga_sur_FULL.MP4:ro \
    -v "$OUTPUT_DIR":/workspace/output \
    -e MODEL_SIZE="$MODEL_SIZE" \
    -e MAX_FRAMES="$MAX_FRAMES" \
    -e SKIP_FRAMES="$SKIP_FRAMES" \
    jetson-depth-anything-v3-trt:latest

echo ""
echo "Processing complete!"
echo ""
echo "Results Summary:"
TOTAL_FILES=$(find "$OUTPUT_DIR" -name "*.jpg" -o -name "*.png" 2>/dev/null | wc -l)
echo "  Total output files: $TOTAL_FILES"
echo "  Frames processed: ~$((TOTAL_FILES / 3))"
echo ""
echo "Output location: $OUTPUT_DIR/turtle_depth_trt/"
