Configuration
=============

Configuration Files
-----------------

The pipeline uses several configuration files to control its behavior:

1. Main Configuration
^^^^^^^^^^^^^^^^^^
Located at ``edge/configs/default_config.yaml``::

    video:
      input_paths:
        - type: local
          path: /workspace/test_videos/*.mp4
      output_path: /output/processed

    inference:
      model_id: "fish-scuba-project/2"
      confidence_threshold: 0.1
      batch_size: 1
      api_url: "http://inference-server:9001"

    processing:
      fps_limit: 5
      export_format: ["json", "csv"]
      timestamp_format: "%Y-%m-%d %H:%M:%S"
      overlay:
        show_fps: true
        show_detections: true
        show_system_stats: true

    system:
      min_memory_gb: 4
      min_cpu_cores: 2
      log_level: "INFO"
      temp_directory: "/tmp/processing"

2. Docker Configuration
^^^^^^^^^^^^^^^^^^^^
Located at ``edge/docker-compose.yml``::

    services:
      inference-server:
        build: ./docker/inference
        ports:
          - "9001:9001"
        environment:
          - ROBOFLOW_API_KEY=${ROBOFLOW_API_KEY}

      jupyterlab:
        build: ./docker/jupyterlab
        ports:
          - "8888:8888"
        volumes:
          - ..:/workspace

Environment Variables
-------------------

Required Variables
^^^^^^^^^^^^^^^^
* ``ROBOFLOW_API_KEY``: Your Roboflow API key
* ``MODEL_ID``: The model ID to use (default: "fish-scuba-project/2")

Optional Variables
^^^^^^^^^^^^^^^^
* ``INFERENCE_SERVER_PORT``: Port for inference server (default: 9001)
* ``JUPYTERLAB_PORT``: Port for JupyterLab (default: 8888)
* ``LOG_LEVEL``: Logging level (default: INFO)

Model Configuration
-----------------

Adding Custom Models
^^^^^^^^^^^^^^^^^
1. Create a new directory in ``models/``
2. Add model files following the structure::

    models/
    ├── model_name/
    │   ├── model.pt
    │   ├── config.yaml
    │   └── metadata.json

3. Update configuration to use the new model

Processing Configuration
---------------------

Video Processing
^^^^^^^^^^^^^^
* ``fps_limit``: Limit processing frame rate
* ``confidence_threshold``: Detection confidence threshold
* ``batch_size``: Batch size for inference

Output Configuration
^^^^^^^^^^^^^^^^^
* ``export_format``: List of export formats (json, csv)
* ``output_path``: Path for processed results
* ``overlay``: Configuration for video overlay

System Requirements
-----------------

Minimum Requirements
^^^^^^^^^^^^^^^^^
* Memory: 4GB RAM
* CPU: 2 cores
* Storage: 20GB available

Recommended Requirements
^^^^^^^^^^^^^^^^^^^^
* Memory: 8GB RAM
* CPU: 4 cores
* Storage: 50GB available
* GPU: NVIDIA Jetson or compatible

Advanced Configuration
-------------------

Performance Tuning
^^^^^^^^^^^^^^^^
* Adjust ``batch_size`` for optimal GPU utilization
* Modify ``fps_limit`` based on processing capabilities
* Configure ``temp_directory`` for fast storage access

Security Configuration
^^^^^^^^^^^^^^^^^^^
* Use environment variables for sensitive data
* Configure network access in docker-compose.yml
* Set appropriate file permissions

Logging Configuration
^^^^^^^^^^^^^^^^^^
* Set ``log_level`` for desired verbosity
* Configure log rotation in production
* Enable system monitoring for long-running processes

