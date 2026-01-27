#!/usr/bin/env python3
"""
Generate TensorRT Engine for Depth-Anything-V3
Optimized for Jetson AGX Orin
"""

import torch
import tensorrt as trt
import numpy as np
from pathlib import Path
import argparse

def create_trt_engine(onnx_path, engine_path, fp16=True):
    """Convert ONNX model to TensorRT engine"""
    
    TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
    
    # Create builder
    builder = trt.Builder(TRT_LOGGER)
    config = builder.create_builder_config()
    
    # Set memory pool
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)  # 1GB
    
    # Enable FP16 precision for better performance
    if fp16:
        config.set_flag(trt.BuilderFlag.FP16)
    
    # Parse ONNX model
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, TRT_LOGGER)
    
    with open(onnx_path, 'rb') as model:
        if not parser.parse(model.read()):
            print('ERROR: Failed to parse the ONNX file.')
            for error in range(parser.num_errors):
                print(parser.get_error(error))
            return None
    
    # Build engine
    print(f"Building TensorRT engine... This may take a while.")
    engine = builder.build_serialized_network(network, config)
    
    if engine is None:
        print("ERROR: Failed to build TensorRT engine")
        return None
    
    # Save engine
    with open(engine_path, 'wb') as f:
        f.write(engine)
    
    print(f"TensorRT engine saved to: {engine_path}")
    return engine_path

def download_depth_anything_v3_model():
    """Download Depth-Anything-V3 model"""
    from transformers import pipeline
    
    print("Downloading Depth-Anything-V3 model...")
    
    # This will download the model to local cache
    depth_estimator = pipeline(
        "depth-estimation",
        model="depth-anything/Depth-Anything-V3-Small-hf",
        device=0 if torch.cuda.is_available() else -1
    )
    
    return depth_estimator

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-size', choices=['small', 'base', 'large'], default='small')
    parser.add_argument('--fp16', action='store_true', default=True)
    args = parser.parse_args()
    
    # Download and prepare model
    model = download_depth_anything_v3_model()
    print("Model ready for TensorRT optimization!")
