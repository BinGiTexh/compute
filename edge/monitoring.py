import time
import psutil
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from base_config import DeviceConfig

class DeviceMonitor:
    def __init__(self, device_type: str = None, log_dir: str = "logs"):
        self.device_config = DeviceConfig(device_type)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Load thresholds from device config
        self.thresholds = self._load_thresholds()
        
    def _setup_logging(self):
        """Configure logging for the monitor."""
        log_file = self.log_dir / f"{self.device_config.device_type}_monitor.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("DeviceMonitor")

    def _load_thresholds(self) -> Dict:
        """Load monitoring thresholds from device config."""
        return {
            "memory": 80,  # Percentage
            "cpu": 90,     # Percentage
            "gpu": 85,     # Percentage
            "temperature": self.device_config.config["constraints"]["thermal_throttle_temp"],
            "disk": 90     # Percentage
        }

    def collect_metrics(self) -> Dict:
        """Collect current device metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "device_type": self.device_config.device_type,
            "memory": self._get_memory_metrics(),
            "cpu": self._get_cpu_metrics(),
            "gpu": self._get_gpu_metrics(),
            "disk": self._get_disk_metrics(),
            "temperature": self._get_temperature_metrics(),
            "power": self._get_power_metrics()
        }
        return metrics

    def _get_memory_metrics(self) -> Dict:
        """Collect memory metrics."""
        vm = psutil.virtual_memory()
        return {
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "percentage": vm.percent
        }

    def _get_cpu_metrics(self) -> Dict:
        """Collect CPU metrics."""
        return {
            "usage_percent": psutil.cpu_percent(interval=1, percpu=True),
            "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            "load_avg": psutil.getloadavg()
        }

    def _get_gpu_metrics(self) -> Dict:
        """Collect GPU metrics if available."""
        if not self.device_config.config["features"]["supports_cuda"]:
            return {"available": False}
        
        try:
            import torch
            return {
                "available": True,
                "memory_allocated": torch.cuda.memory_allocated(),
                "memory_reserved": torch.cuda.memory_reserved(),
                "utilization": self._get_gpu_utilization()
            }
        except:
            return {"available": False}

    def _get_gpu_utilization(self) -> Optional[float]:
        """Get GPU utilization using nvidia-smi."""
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True
            )
            return float(result.stdout.strip())
        except:
            return None

    def _get_disk_metrics(self) -> Dict:
        """Collect disk metrics."""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percentage": disk.percent
        }

    def _get_temperature_metrics(self) -> Optional[float]:
        """Get temperature metrics if available."""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Get the first temperature reading
                first_sensor = next(iter(temps.values()))
                return first_sensor[0].current
            return None
        except:
            return None

    def _get_power_metrics(self) -> Dict:
        """Get power metrics if available."""
        try:
            import subprocess
            if self.device_config.device_type.startswith('jetson'):
                result = subprocess.run(
                    ['tegrastats'],
                    capture_output=True,
                    text=True
                )
                # Parse tegrastats output for power information
                return {"power_draw": "Parse tegrastats output here"}
            return {}
        except:
            return {}

    def check_thresholds(self, metrics: Dict) -> List[str]:
        """Check if any metrics exceed their thresholds."""
        warnings = []
        
        # Check memory
        if metrics["memory"]["percentage"] > self.thresholds["memory"]:
            warnings.append(f"Memory usage ({metrics['memory']['percentage']}%) exceeds threshold")
        
        # Check CPU
        cpu_avg = sum(metrics["cpu"]["usage_percent"]) / len(metrics["cpu"]["usage_percent"])
        if cpu_avg > self.thresholds["cpu"]:
            warnings.append(f"CPU usage ({cpu_avg}%) exceeds threshold")
        
        # Check GPU if available
        if metrics["gpu"]["available"] and metrics["gpu"]["utilization"]:
            if metrics["gpu"]["utilization"] > self.thresholds["gpu"]:
                warnings.append(f"GPU usage ({metrics['gpu']['utilization']}%) exceeds threshold")
        
        # Check temperature
        if metrics["temperature"] and metrics["temperature"] > self.thresholds["temperature"]:
            warnings.append(f"Temperature ({metrics['temperature']}°C) exceeds threshold")
        
        return warnings

    def start_monitoring(self, interval: int = 60):
        """Start continuous monitoring with specified interval."""
        self.logger.info(f"Starting monitoring for {self.device_config.device_type}")
        
        try:
            while True:
                metrics = self.collect_metrics()
                warnings = self.check_thresholds(metrics)
                
                # Log metrics
                metrics_file = self.log_dir / f"{self.device_config.device_type}_metrics.json"
                with open(metrics_file, 'a') as f:
                    json.dump(metrics, f)
                    f.write('\n')
                
                # Log warnings
                for warning in warnings:
                    self.logger.warning(warning)
                
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Monitoring error: {str(e)}")

if __name__ == "__main__":
    # Example usage
    monitor = DeviceMonitor()
    current_metrics = monitor.collect_metrics()
    print(json.dumps(current_metrics, indent=2))
    
    # Start continuous monitoring
    # monitor.start_monitoring(interval=60)
