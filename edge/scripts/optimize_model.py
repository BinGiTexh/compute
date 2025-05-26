import argparse
import torch
import numpy as np
import os
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from base_config import DeviceConfig

class ModelOptimizer:
    def __init__(self, device_type: str = None):
        self.device_config = DeviceConfig(device_type)
        self.output_dir = Path("optimized_models")
        self.output_dir.mkdir(exist_ok=True)

    def optimize_for_device(self, model_path: str) -> Path:
        """Optimize model for specific device type."""
        device_features = self.device_config.get_device_features()
        
        if device_features["supports_tensorrt"]:
            return self._optimize_tensorrt(model_path)
        elif device_features["supports_cuda"]:
            return self._optimize_cuda(model_path)
        else:
            return self._optimize_cpu(model_path)

    def _optimize_tensorrt(self, model_path: str) -> Path:
        """Optimize model using TensorRT."""
        try:
            import tensorrt as trt
            
            print(f"Optimizing model for TensorRT on {self.device_config.device_type}")
            
            # Load model
            model = torch.load(model_path)
            
            # Export to ONNX first
            onnx_path = self.output_dir / "temp.onnx"
            torch.onnx.export(model, torch.randn(1, 3, 224, 224), onnx_path)
            
            # Convert to TensorRT
            logger = trt.Logger(trt.Logger.WARNING)
            builder = trt.Builder(logger)
            network = builder.create_network()
            parser = trt.OnnxParser(network, logger)
            
            with open(onnx_path, 'rb') as f:
                parser.parse(f.read())
            
            config = builder.create_builder_config()
            config.max_workspace_size = 1 << 30  # 1GB
            
            if self.device_config.config["features"]["supports_fp16"]:
                config.set_flag(trt.BuilderFlag.FP16)
            
            engine = builder.build_engine(network, config)
            
            # Save engine
            output_path = self.output_dir / f"{Path(model_path).stem}_tensorrt.engine"
            with open(output_path, 'wb') as f:
                f.write(engine.serialize())
            
            # Cleanup
            os.remove(onnx_path)
            
            return output_path
        
        except ImportError:
            print("TensorRT not available, falling back to CUDA optimization")
            return self._optimize_cuda(model_path)

    def _optimize_cuda(self, model_path: str) -> Path:
        """Optimize model for CUDA execution."""
        print(f"Optimizing model for CUDA on {self.device_config.device_type}")
        
        # Load model
        model = torch.load(model_path)
        
        # Convert to torch.jit
        example_input = torch.randn(1, 3, 224, 224)
        traced_model = torch.jit.trace(model, example_input)
        
        # Optimize for inference
        traced_model.eval()
        if self.device_config.config["features"]["supports_fp16"]:
            traced_model = traced_model.half()
        
        # Save optimized model
        output_path = self.output_dir / f"{Path(model_path).stem}_cuda.pt"
        torch.jit.save(traced_model, output_path)
        
        return output_path

    def _optimize_cpu(self, model_path: str) -> Path:
        """Optimize model for CPU execution."""
        print(f"Optimizing model for CPU on {self.device_config.device_type}")
        
        # Load model
        model = torch.load(model_path, map_location='cpu')
        
        # Convert to quantized model
        quantized_model = torch.quantization.quantize_dynamic(
            model, {torch.nn.Linear, torch.nn.Conv2d}, dtype=torch.qint8
        )
        
        # Convert to torch.jit for better CPU performance
        example_input = torch.randn(1, 3, 224, 224)
        traced_model = torch.jit.trace(quantized_model, example_input)
        
        # Save optimized model
        output_path = self.output_dir / f"{Path(model_path).stem}_cpu.pt"
        torch.jit.save(traced_model, output_path)
        
        return output_path

    def optimize_batch_size(self, model_path: str) -> int:
        """Determine optimal batch size for the device."""
        return self.device_config.get_optimized_batch_size()

    def get_optimization_summary(self, original_path: str, optimized_path: str) -> dict:
        """Generate optimization summary."""
        original_size = os.path.getsize(original_path)
        optimized_size = os.path.getsize(optimized_path)
        
        return {
            "device_type": self.device_config.device_type,
            "original_model": {
                "path": str(original_path),
                "size_bytes": original_size
            },
            "optimized_model": {
                "path": str(optimized_path),
                "size_bytes": optimized_size
            },
            "size_reduction": f"{(1 - optimized_size/original_size) * 100:.2f}%",
            "recommended_batch_size": self.optimize_batch_size(original_path),
            "device_features": self.device_config.get_device_features()
        }

def main():
    parser = argparse.ArgumentParser(description="Optimize ML models for specific devices")
    parser.add_argument("--model", type=str, required=True, help="Path to the model file")
    parser.add_argument("--device", type=str, help="Target device type")
    args = parser.parse_args()

    optimizer = ModelOptimizer(args.device)
    optimized_path = optimizer.optimize_for_device(args.model)
    
    summary = optimizer.get_optimization_summary(args.model, optimized_path)
    print("\nOptimization Summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
