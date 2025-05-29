Running the Pipeline
==================

This guide explains how to run the video processing pipeline in different modes.

Basic Usage
----------

Command Line Interface
^^^^^^^^^^^^^^^^^^^
Process a single video file::

    python scripts/process_video.py \
      --config configs/default_config.yaml \
      --video path/to/video.mp4 \
      --model-id "fish-scuba-project/2" \
      --confidence 0.1

JupyterLab Interface
^^^^^^^^^^^^^^^^^
1. Open JupyterLab at http://localhost:8888
2. Navigate to notebooks/templates/
3. Open video_analysis_template.ipynb
4. Modify parameters as needed
5. Run all cells

Batch Processing
--------------

Processing Multiple Videos
^^^^^^^^^^^^^^^^^^^^^^
Using wildcards::

    python scripts/process_video.py \
      --config configs/default_config.yaml \
      --video "data/videos/*.mp4"

Using a file list::

    python scripts/process_video.py \
      --config configs/default_config.yaml \
      --video-list videos.txt

GitHub Actions
^^^^^^^^^^^^
1. Push videos to the repository
2. Go to Actions tab
3. Select "Video Processing Pipeline"
4. Click "Run workflow"
5. Enter video path
6. Monitor progress
7. Download results from artifacts

Real-time Processing
-----------------

USB Camera Input
^^^^^^^^^^^^^
Process live video feed::

    python scripts/process_video.py \
      --config configs/default_config.yaml \
      --device 0  # Use camera index

Network Stream
^^^^^^^^^^^^
Process RTSP stream::

    python scripts/process_video.py \
      --config configs/default_config.yaml \
      --url rtsp://camera-url

Monitoring Progress
----------------

Console Output
^^^^^^^^^^^^
The pipeline provides real-time progress information::

    Processing video: video.mp4
    Frame 100/500 (20%) | FPS: 25 | Detections: 15
    CPU: 45% | Memory: 2.5GB | GPU: 80%

Web Interface
^^^^^^^^^^^
Monitor through JupyterLab:

1. Open the processing notebook
2. View real-time plots
3. Check system metrics
4. View detection visualizations

Log Files
^^^^^^^^
Check logs for detailed information::

    tail -f logs/processing.log

Error Handling
------------

Common Errors
^^^^^^^^^^^
1. Video format not supported::

    # Convert video to supported format
    ffmpeg -i input.avi output.mp4

2. Out of memory::

    # Reduce batch size in config
    # or
    # Reduce video resolution

3. Model errors::

    # Check API key
    # Verify model ID
    # Test inference server

Recovery
^^^^^^^
The pipeline implements automatic recovery:

* Saves progress every 100 frames
* Resumes from last checkpoint
* Preserves partial results

Best Practices
------------

Performance Optimization
^^^^^^^^^^^^^^^^^^^^
1. Pre-process videos::

    ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4

2. Adjust batch size based on GPU memory
3. Use appropriate confidence threshold
4. Enable system monitoring

Resource Management
^^^^^^^^^^^^^^^^
1. Monitor system resources
2. Clean up temporary files
3. Archive processed results
4. Implement log rotation

Production Deployment
^^^^^^^^^^^^^^^^^^
1. Use environment variables
2. Configure error notifications
3. Implement monitoring
4. Set up backup procedures

