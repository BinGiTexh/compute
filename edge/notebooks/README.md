# Notebook Classification System

This directory contains notebooks organized by their resource requirements and device compatibility.

## Directory Structure

- `full-inference/`: Notebooks requiring significant computational resources
  - Suitable for Jetson AGX Orin and other high-performance devices
  - Typically requires GPU with 8GB+ memory
  - Full-resolution inference and complex model architectures

- `light-inference/`: Optimized notebooks for less powerful devices
  - Compatible with Jetson Nano and Raspberry Pi
  - Optimized for devices with limited resources
  - Uses quantized models and efficient inference techniques

- `shared/`: Device-agnostic utility notebooks
  - Common preprocessing functions
  - Data visualization tools
  - Configuration utilities
  - Device compatibility checking

## Notebook Metadata Tags

Each notebook should include the following metadata in the first cell:

```json
{
    "device_requirements": {
        "min_memory": "2GB",
        "gpu_required": true/false,
        "min_cuda_capability": "5.0",
        "recommended_device_type": ["jetson-agx-orin", "jetson-nano", "raspberry-pi"],
        "max_batch_size": 32
    }
}
```

## Best Practices

1. Always check device compatibility at notebook startup
2. Include memory requirement estimates
3. Provide fallback options for lower-resource devices
4. Document any device-specific optimizations
