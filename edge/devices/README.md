# Device-Specific Configurations

This directory contains configurations and setup instructions for different edge computing devices supported by the project.

## Supported Devices

### 1. Jetson AGX Orin
- **Hardware Specifications:**
  - RAM: 32GB
  - CPU: 12-core ARM v8.2
  - GPU: 2048 CUDA cores
  - Storage: NVMe SSD recommended

**Setup Instructions:**
```bash
# Install system dependencies
sudo apt-get update && sudo apt-get install -y python3-pip cmake

# Install Python dependencies
pip install -r jetson-agx-orin/requirements.txt

# Set environment variables
export CUDA_HOME=/usr/local/cuda
export PATH=$PATH:$CUDA_HOME/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64
```

### 2. Jetson Nano
- **Hardware Specifications:**
  - RAM: 4GB
  - CPU: 4-core ARM v8
  - GPU: 128 CUDA cores
  - Storage: microSD/NVMe

**Setup Instructions:**
```bash
# Install system dependencies
sudo apt-get update && sudo apt-get install -y python3-pip cmake

# Install Python dependencies
pip install -r jetson-nano/requirements.txt

# Set memory optimization variables
export PYTORCH_JIT=0
export CUDA_LAUNCH_BLOCKING=1
```

### 3. Raspberry Pi
- **Hardware Specifications:**
  - RAM: 4GB/8GB
  - CPU: ARM v8 quad-core
  - GPU: VideoCore VI
  - Storage: microSD

**Setup Instructions:**
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip cmake libjpeg-dev zlib1g-dev

# Install Python dependencies
pip install -r raspberry-pi/requirements.txt

# Enable memory optimization
export OPENBLAS_NUM_THREADS=2
export MKL_NUM_THREADS=2
```

## Configuration Files

Each device directory contains:
- `environment.yml`: Conda/Micromamba environment configuration
- `requirements.txt`: Python package requirements
- `device_config.json`: Device-specific settings and constraints

## Resource Management

### Memory Thresholds
- Jetson AGX Orin: Up to 24GB for ML tasks
- Jetson Nano: Up to 3GB for ML tasks
- Raspberry Pi: Up to 6GB for ML tasks

### Batch Size Guidelines
- Jetson AGX Orin: Up to 64
- Jetson Nano: Up to 8
- Raspberry Pi: 1 (no batching)

## Performance Optimization

### Model Quantization
- Jetson devices: Support FP16 and INT8
- Raspberry Pi: INT8 quantization recommended

### Framework Optimization
- Jetson devices: TensorRT acceleration
- Raspberry Pi: TFLite and ONNX Runtime optimization

## Monitoring and Maintenance

### Temperature Thresholds
- Jetson AGX Orin: 85°C max
- Jetson Nano: 80°C max
- Raspberry Pi: 75°C max

### Resource Monitoring
Use `health-check.sh` script with appropriate device flag:
```bash
./health-check.sh --device=<device-type>
```

## Troubleshooting

### Common Issues
1. Memory Errors
   - Check `max_batch_size` in device_config.json
   - Monitor memory usage with `monitoring.py`
   - Reduce model size or use quantization

2. Temperature Warnings
   - Ensure proper ventilation
   - Check thermal throttling settings
   - Reduce workload if necessary

3. Performance Issues
   - Verify correct CUDA/TensorRT installation
   - Check power mode settings
   - Monitor system resources

## Adding New Devices

To add support for a new device:
1. Create a new directory under `devices/`
2. Copy and modify configuration templates
3. Add device-specific optimizations
4. Update test suite for new device
5. Document setup and maintenance procedures

