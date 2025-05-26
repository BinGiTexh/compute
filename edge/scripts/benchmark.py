import argparse
import json
import time
from pathlib import Path
import numpy as np
from typing import Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from base_config import DeviceConfig
from monitoring import DeviceMonitor

class DeviceBenchmark:
    def __init__(self, device_type: str = None):
        self.device_config = DeviceConfig(device_type)
        self.monitor = DeviceMonitor(device_type)
        self.results_dir = Path("test-results")
        self.results_dir.mkdir(exist_ok=True)

    def run_memory_benchmark(self) -> Dict:
        """Test memory allocation and access speeds."""
        sizes = [1024, 1024*1024, 1024*1024*10]  # Different array sizes
        results = []

        for size in sizes:
            start_time = time.time()
            arr = np.random.rand(size)
            allocation_time = time.time() - start_time

            start_time = time.time()
            _ = arr.sum()
            access_time = time.time() - start_time

            results.append({
                "size_bytes": size * 8,
                "allocation_time": allocation_time,
                "access_time": access_time
            })

        return {"memory_benchmark": results}

    def run_cpu_benchmark(self) -> Dict:
        """Test CPU performance with different workloads."""
        results = []
        
        # Matrix multiplication benchmark
        sizes = [(100, 100), (500, 500), (1000, 1000)]
        for size in sizes:
            a = np.random.rand(*size)
            b = np.random.rand(*size)
            
            start_time = time.time()
            _ = np.dot(a, b)
            computation_time = time.time() - start_time
            
            results.append({
                "operation": "matrix_multiplication",
                "size": size,
                "time": computation_time
            })

        return {"cpu_benchmark": results}

    def run_gpu_benchmark(self) -> Dict:
        """Test GPU performance if available."""
        if not self.device_config.config["features"]["supports_cuda"]:
            return {"gpu_benchmark": {"available": False}}

        try:
            import torch
            results = []

            sizes = [(1000, 1000), (2000, 2000), (4000, 4000)]
            for size in sizes:
                # CPU tensor creation
                a = torch.rand(*size)
                b = torch.rand(*size)

                # GPU transfer timing
                start_time = time.time()
                a_gpu = a.cuda()
                b_gpu = b.cuda()
                transfer_time = time.time() - start_time

                # GPU computation timing
                start_time = time.time()
                _ = torch.matmul(a_gpu, b_gpu)
                computation_time = time.time() - start_time

                results.append({
                    "size": size,
                    "transfer_time": transfer_time,
                    "computation_time": computation_time
                })

            return {"gpu_benchmark": {"available": True, "results": results}}
        except Exception as e:
            return {"gpu_benchmark": {"available": False, "error": str(e)}}

    def run_disk_benchmark(self) -> Dict:
        """Test disk I/O performance."""
        results = []
        sizes = [1024*1024, 1024*1024*10, 1024*1024*100]  # 1MB, 10MB, 100MB

        for size in sizes:
            data = os.urandom(size)
            
            # Write test
            start_time = time.time()
            with open("test.bin", "wb") as f:
                f.write(data)
            write_time = time.time() - start_time
            
            # Read test
            start_time = time.time()
            with open("test.bin", "rb") as f:
                _ = f.read()
            read_time = time.time() - start_time
            
            results.append({
                "size_bytes": size,
                "write_time": write_time,
                "read_time": read_time
            })

        # Cleanup
        if os.path.exists("test.bin"):
            os.remove("test.bin")

        return {"disk_benchmark": results}

    def run_all_benchmarks(self) -> Dict:
        """Run all benchmarks and collect results."""
        start_time = time.time()
        
        results = {
            "device_type": self.device_config.device_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "device_info": self.device_config.config,
            "benchmarks": {
                **self.run_memory_benchmark(),
                **self.run_cpu_benchmark(),
                **self.run_gpu_benchmark(),
                **self.run_disk_benchmark()
            },
            "total_time": time.time() - start_time
        }

        # Save results
        results_file = self.results_dir / f"benchmark_{self.device_config.device_type}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        return results

def main():
    parser = argparse.ArgumentParser(description="Run device-specific benchmarks")
    parser.add_argument("--device", type=str, help="Device type to benchmark")
    args = parser.parse_args()

    benchmark = DeviceBenchmark(args.device)
    results = benchmark.run_all_benchmarks()
    
    print("\nBenchmark Results Summary:")
    print("-" * 40)
    print(f"Device Type: {results['device_type']}")
    print(f"Total Time: {results['total_time']:.2f} seconds")
    
    if results['benchmarks']['gpu_benchmark'].get('available', False):
        print("\nGPU Performance:")
        gpu_results = results['benchmarks']['gpu_benchmark']['results']
        for result in gpu_results:
            print(f"Size {result['size']}: {result['computation_time']:.4f}s")
    
    print("\nCPU Performance:")
    cpu_results = results['benchmarks']['cpu_benchmark']
    for result in cpu_results:
        print(f"Matrix {result['size']}: {result['time']:.4f}s")

if __name__ == "__main__":
    main()
