import json
import os
import platform
import psutil
import torch
from pathlib import Path
from typing import Dict, Optional

class DeviceConfig:
    def __init__(self, device_type: str = None):
        self.base_path = Path("devices")
        self.device_type = device_type or self._detect_device_type()
        self.config = self._load_config()
        
    def _detect_device_type(self) -> str:
        """Auto-detect device type based on system characteristics."""
        # Check for NVIDIA Jetson
        if os.path.exists("/proc/device-tree/model"):
            with open("/proc/device-tree/model", "r") as f:
                model = f.read()
                if "AGX Orin" in model:
                    return "jetson-agx-orin"
                elif "Nano" in model:
                    return "jetson-nano"
        
        # Check for Raspberry Pi
        if os.path.exists("/proc/device-tree/model"):
            with open("/proc/device-tree/model", "r") as f:
                if "Raspberry Pi" in f.read():
                    return "raspberry-pi"
        
        return "jetson-agx-orin"  # Default to AGX Orin

    def _load_config(self) -> Dict:
        """Load device-specific configuration."""
        config_path = self.base_path / self.device_type / "device_config.json"
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Configuration not found for device type: {self.device_type}")

    def get_resource_limits(self) -> Dict:
        """Get current resource limits and usage."""
        return {
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "limit": self.config["resources"]["memory"]["max_allocation"]
            },
            "cpu": {
                "cores": psutil.cpu_count(),
                "usage": psutil.cpu_percent(),
                "limit": self.config["constraints"]["recommended_thread_count"]
            },
            "gpu": self._get_gpu_info()
        }

    def _get_gpu_info(self) -> Dict:
        """Get GPU information if available."""
        if not self.config["features"]["supports_cuda"]:
            return {"available": False}
        
        try:
            return {
                "available": torch.cuda.is_available(),
                "device_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
                "device_name": torch.cuda.get_device_name(),
                "memory_allocated": torch.cuda.memory_allocated(),
                "memory_reserved": torch.cuda.memory_reserved()
            }
        except:
            return {"available": False}

    def check_notebook_compatibility(self, requirements: Dict) -> bool:
        """Check if the current device meets notebook requirements."""
        if requirements.get("gpu_required") and not self.config["features"]["supports_cuda"]:
            return False
        
        if requirements.get("min_memory"):
            required_memory = self._parse_memory_string(requirements["min_memory"])
            available_memory = self._parse_memory_string(self.config["resources"]["memory"]["max_allocation"])
            if required_memory > available_memory:
                return False
        
        return True

    def _parse_memory_string(self, memory_str: str) -> int:
        """Convert memory string (e.g., '2GB') to bytes."""
        units = {"KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
        number = float(''.join(filter(str.isdigit, memory_str)))
        unit = ''.join(filter(str.isalpha, memory_str.upper()))
        return int(number * units.get(unit, 1))

    def get_optimized_batch_size(self) -> int:
        """Get recommended batch size based on device capabilities."""
        return self.config["constraints"]["max_batch_size"]

    def get_device_features(self) -> Dict:
        """Get supported features for the current device."""
        return self.config["features"]

if __name__ == "__main__":
    # Example usage
    config = DeviceConfig()
    print(f"Detected device type: {config.device_type}")
    print("\nResource limits:")
    print(json.dumps(config.get_resource_limits(), indent=2))
    print("\nDevice features:")
    print(json.dumps(config.get_device_features(), indent=2))
