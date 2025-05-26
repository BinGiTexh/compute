import unittest
import sys
import os
from pathlib import Path
import json
import pytest

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from base_config import DeviceConfig
from monitoring import DeviceMonitor

class TestDeviceCompatibility(unittest.TestCase):
    def setUp(self):
        """Set up test cases with different device configurations."""
        self.device_types = ["jetson-agx-orin", "jetson-nano", "raspberry-pi"]
        self.configs = {
            device_type: DeviceConfig(device_type) 
            for device_type in self.device_types
        }

    def test_device_detection(self):
        """Test automatic device detection logic."""
        config = DeviceConfig()
        self.assertIn(config.device_type, self.device_types)

    def test_config_loading(self):
        """Test that all device configurations load correctly."""
        for device_type, config in self.configs.items():
            self.assertIsNotNone(config.config)
            self.assertEqual(config.config["device_type"], device_type)

    def test_resource_limits(self):
        """Test resource limit validation for each device."""
        for device_type, config in self.configs.items():
            limits = config.get_resource_limits()
            self.assertIn("memory", limits)
            self.assertIn("cpu", limits)
            self.assertIn("gpu", limits)

    def test_notebook_compatibility(self):
        """Test notebook compatibility checking."""
        test_requirements = {
            "gpu_required": True,
            "min_memory": "4GB",
            "min_cuda_capability": "5.0"
        }
        
        # AGX Orin should be compatible
        self.assertTrue(
            self.configs["jetson-agx-orin"].check_notebook_compatibility(test_requirements)
        )
        
        # Raspberry Pi should not be compatible (no GPU)
        self.assertFalse(
            self.configs["raspberry-pi"].check_notebook_compatibility(test_requirements)
        )

    @pytest.mark.skipif(
        not DeviceConfig().config["features"]["supports_cuda"],
        reason="Test requires GPU support"
    )
    def test_gpu_features(self):
        """Test GPU-specific features."""
        config = self.configs["jetson-agx-orin"]
        features = config.get_device_features()
        self.assertTrue(features["supports_cuda"])
        self.assertTrue(features["supports_tensorrt"])

    def test_monitoring_thresholds(self):
        """Test device-specific monitoring thresholds."""
        for device_type in self.device_types:
            monitor = DeviceMonitor(device_type)
            metrics = monitor.collect_metrics()
            warnings = monitor.check_thresholds(metrics)
            self.assertIsInstance(warnings, list)

    def test_memory_parsing(self):
        """Test memory string parsing for different formats."""
        config = self.configs["jetson-agx-orin"]
        test_cases = [
            ("2GB", 2 * 1024**3),
            ("512MB", 512 * 1024**2),
            ("1TB", 1024**4),
            ("1024KB", 1024 * 1024)
        ]
        for memory_str, expected_bytes in test_cases:
            self.assertEqual(
                config._parse_memory_string(memory_str),
                expected_bytes
            )

    def test_batch_size_optimization(self):
        """Test batch size recommendations for different devices."""
        batch_sizes = {
            device_type: config.get_optimized_batch_size()
            for device_type, config in self.configs.items()
        }
        
        # AGX Orin should support larger batches than Nano
        self.assertGreater(
            batch_sizes["jetson-agx-orin"],
            batch_sizes["jetson-nano"]
        )

    def test_device_specific_constraints(self):
        """Test device-specific constraints are properly enforced."""
        for device_type, config in self.configs.items():
            constraints = config.config["constraints"]
            self.assertIn("max_batch_size", constraints)
            self.assertIn("recommended_thread_count", constraints)
            self.assertIn("thermal_throttle_temp", constraints)

if __name__ == '__main__':
    unittest.main()
