Troubleshooting
==============

This guide helps you diagnose and resolve common issues with the video processing pipeline.

System Issues
------------

Docker Problems
^^^^^^^^^^^^

1. Container Won't Start
   ::

    # Check Docker logs
    docker compose logs

    # Common solutions:
    # - Verify Docker service is running
    # - Check port conflicts
    # - Ensure sufficient system resources

2. GPU Not Available
   ::

    # Verify NVIDIA runtime
    docker info | grep -i nvidia

    # Check NVIDIA driver
    nvidia-smi

    # Solutions:
    # - Install NVIDIA drivers
    # - Configure NVIDIA Container Runtime
    # - Update Docker configuration

3. Permission Issues
   ::

    # Add user to docker group
    sudo usermod -aG docker $USER

    # Fix directory permissions
    sudo chown -R $USER:$USER /path/to/data

Processing Issues
---------------

Video Input Problems
^^^^^^^^^^^^^^^^

1. Video Not Found
   ::

    # Check file existence and permissions
    ls -l /path/to/video.mp4

    # Verify path in config
    cat configs/default_config.yaml

2. Unsupported Format
   ::

    # Check video format
    ffmpeg -i video.mp4

    # Convert to supported format
    ffmpeg -i input.avi -c:v libx264 output.mp4

3. Corrupted Video
   ::

    # Verify video integrity
    ffmpeg -v error -i video.mp4 -f null - 2>error.log

Model Issues
-----------

1. Model Loading Errors
   ::

    # Check model files
    ls -l models/

    # Verify API key
    echo $ROBOFLOW_API_KEY

    # Solutions:
    # - Download model files
    # - Update API key
    # - Check model ID

2. Inference Errors
   ::

    # Check inference server logs
    docker compose logs inference-server

    # Test inference server
    curl http://localhost:9001/health

3. Poor Detection Results
   ::

    # Adjust confidence threshold
    # Check video quality
    # Verify model compatibility

Performance Issues
----------------

1. Slow Processing
   ::

    # Check resource usage
    top
    nvidia-smi

    # Solutions:
    # - Reduce batch size
    # - Lower video resolution
    # - Adjust FPS limit

2. Memory Issues
   ::

    # Monitor memory
    free -h
    nvidia-smi

    # Solutions:
    # - Clear cache
    # - Reduce batch size
    # - Process in chunks

3. GPU Problems
   ::

    # Check GPU status
    nvidia-smi -l 1

    # Solutions:
    # - Update drivers
    # - Reduce workload
    # - Check cooling

Output Issues
------------

1. Missing Results
   ::

    # Check output directory
    ls -l output/

    # Verify permissions
    whoami
    groups

2. Corrupted Files
   ::

    # Validate JSON
    python -m json.tool output/results.json

    # Check CSV format
    head -n 5 output/results.csv

3. Incomplete Results
   ::

    # Check processing logs
    cat logs/processing.log

    # Verify completion status
    tail -n 50 logs/processing.log

Network Issues
-------------

1. API Connection
   ::

    # Test network
    ping api.roboflow.com

    # Check proxy settings
    env | grep -i proxy

2. Service Communication
   ::

    # Test internal network
    docker network ls
    docker network inspect edge_default

3. Port Conflicts
   ::

    # Check port usage
    sudo netstat -tulpn

    # Update port configuration
    vim docker-compose.yml

Recovery Procedures
-----------------

1. Data Recovery
   ::

    # Check backup files
    ls -l output/backup/

    # Restore from backup
    cp output/backup/* output/

2. Service Recovery
   ::

    # Restart services
    docker compose down
    docker compose up -d

3. System Reset
   ::

    # Clean environment
    docker compose down -v
    ./setup.sh

Getting Support
-------------

1. Gathering Information
   ::

    # System info
    uname -a
    docker version
    nvidia-smi

    # Logs
    tar -czf logs.tar.gz logs/

2. Reporting Issues
   - Include system information
   - Attach relevant logs
   - Describe steps to reproduce
   - List attempted solutions

3. Community Resources
   - GitHub Issues
   - Documentation
   - Support Forums
   - Community Discord

