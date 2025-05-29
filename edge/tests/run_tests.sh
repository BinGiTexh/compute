#!/bin/bash

# Exit on error
set -e

echo "Running test suite..."

# Create test video
echo "Creating test video..."
python3 test_video.py

# Run system tests
echo "Running system tests..."
python3 system_test.py --verbose

# Run video processing test
echo "Testing video processing..."
python3 ../scripts/process_video.py \
  --config ../configs/default_config.yaml \
  --video test_videos/test_diver_video.mp4

# Export and validate results
echo "Testing result export..."
python3 ../scripts/export_results.py \
  --input ../output/processing_results.json \
  --output-dir ../output

# Check if required files were created
required_files=(
    "../output/processing_results.json"
    "../output/test_diver_video_detections.csv"
    "../output/test_diver_video_summary.json"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: Required output file not found: $file"
        exit 1
    fi
done

# Validate JSON output
echo "Validating JSON output..."
python3 -c "
import json
with open('../output/processing_results.json') as f:
    data = json.load(f)
assert 'video_info' in data, 'Missing video info'
assert 'processing_info' in data, 'Missing processing info'
assert 'frame_results' in data, 'Missing frame results'
"

# Print test summary from system tests
if [ -f "test_results.json" ]; then
    echo "Test Results Summary:"
    python3 -c "
    import json
    with open('test_results.json') as f:
        data = json.load(f)
    print(f'Total Tests: {data[\"summary\"][\"total\"]}')
    print(f'Passed: {data[\"summary\"][\"passed\"]}')
    print(f'Failed: {data[\"summary\"][\"failed\"]}')
    "
fi

echo "All tests completed successfully!"
