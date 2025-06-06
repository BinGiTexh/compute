# Troubleshooting Guide

## System Requirements

- NVIDIA Jetson device
- JetPack 5.0+
- Minimum 8GB RAM
- Available GPU memory
- Docker with NVIDIA runtime

## Common Issues and Solutions

### Memory Management

1. **Container Memory Issues**
   - Symptoms: OOM kills, slow processing
   - Solutions:
     ```bash
     # Adjust container memory limits
     docker run --memory=8g --memory-swap=16g
     
     # Reduce image size in test_resize.py
     MAX_SIZE = 512  # or lower
     ```

2. **GPU Memory Issues**
   - Symptoms: CUDA out of memory
   - Solutions:
     - Clear CUDA cache in script
     - Process fewer images simultaneously
     - Reduce model precision

### Docker Configuration

1. **NVIDIA Runtime Issues**
   ```bash
   # Verify NVIDIA runtime
   sudo nvidia-ctk runtime configure --runtime=docker
   
   # Restart Docker
   sudo systemctl restart docker
   ```

2. **Permission Issues**
   ```bash
   # Fix Docker socket permissions
   sudo chmod 666 /var/run/docker.sock
   
   # Add user to Docker group
   sudo usermod -aG docker $USER
   ```

### Image Processing

1. **Input/Output Errors**
   - Check directory permissions
   - Verify volume mounts
   - Ensure correct file formats

2. **Model Loading Issues**
   - Verify internet connection
   - Check HuggingFace token
   - Validate model cache

## Performance Optimization

1. **Processing Speed**
   - Use appropriate batch sizes
   - Enable GPU acceleration
   - Optimize image resizing

2. **Memory Usage**
   - Monitor with `nvidia-smi`
   - Use `docker stats`
   - Profile Python memory usage
