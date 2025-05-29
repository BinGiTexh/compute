#!/usr/bin/env python3

import argparse
import json
import os
import requests
import sys
import time
from pathlib import Path

class SystemTest:
    def __init__(self):
        self.inference_url = "http://localhost:9001"
        self.jupyterlab_url = "http://localhost:8888"
        self.test_dir = Path(__file__).parent
        self.results = {
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }

    def run_test(self, name: str, test_func) -> bool:
        """Run a single test and record result."""
        print(f"\nRunning test: {name}")
        start_time = time.time()
        try:
            test_func()
            success = True
            print(f"✓ {name} passed")
        except Exception as e:
            success = False
            print(f"✗ {name} failed: {str(e)}")
        
        duration = time.time() - start_time
        self.results["tests"].append({
            "name": name,
            "success": success,
            "duration": round(duration, 2)
        })
        
        self.results["summary"]["total"] += 1
        if success:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
        
        return success

    def test_inference_server(self):
        """Test inference server health and basic functionality."""
        # Check health endpoint
        response = requests.get(f"{self.inference_url}/health")
        assert response.status_code == 200, "Health check failed"
        
        # Create and send test image
        import cv2
        import numpy as np
        
        # Create simple test image
        img = np.zeros((640, 640, 3), dtype=np.uint8)
        cv2.rectangle(img, (100, 100), (500, 500), (255, 255, 255), -1)
        
        # Save and send image
        test_image = self.test_dir / "test_image.jpg"
        cv2.imwrite(str(test_image), img)
        
        with open(test_image, 'rb') as f:
            response = requests.post(
                f"{self.inference_url}/predict",
                files={"file": f}
            )
        
        assert response.status_code == 200, "Prediction request failed"
        result = response.json()
        assert 'predictions' in result, "Invalid prediction response"
        
        # Cleanup
        test_image.unlink()

    def test_jupyterlab(self):
        """Test JupyterLab accessibility."""
        response = requests.get(self.jupyterlab_url)
        assert response.status_code == 200, "JupyterLab not accessible"

    def test_model_download(self):
        """Test model download functionality."""
        api_key = os.environ.get('ROBOFLOW_API_KEY')
        assert api_key, "ROBOFLOW_API_KEY not set"
        
        from inference_sdk import InferenceHTTPClient
        client = InferenceHTTPClient(api_key=api_key)
        
        # Test model info retrieval
        model_info = client.get_model_info("fish-scuba-project/2")
        assert model_info, "Failed to get model info"

    def test_video_processing(self):
        """Test complete video processing pipeline."""
        # Create test video
        import sys
        sys.path.append(str(self.test_dir))
        import test_video
        
        video_path = self.test_dir / "test_videos" / "test_diver_video.mp4"
        test_video.create_test_video(str(video_path))
        
        assert video_path.exists(), "Failed to create test video"
        
        # Process video
        cmd = f"python3 {self.test_dir.parent}/scripts/process_video.py " \
              f"--config {self.test_dir.parent}/configs/default_config.yaml " \
              f"--video {video_path}"
        
        result = os.system(cmd)
        assert result == 0, "Video processing failed"

    def run_all_tests(self):
        """Run all system tests."""
        print("Starting system tests...")
        
        self.run_test("Inference Server", self.test_inference_server)
        self.run_test("JupyterLab", self.test_jupyterlab)
        self.run_test("Model Download", self.test_model_download)
        self.run_test("Video Processing", self.test_video_processing)
        
        # Save results
        with open(self.test_dir / "test_results.json", 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Print summary
        print("\nTest Summary:")
        print(f"Total Tests: {self.results['summary']['total']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        
        return self.results['summary']['failed'] == 0

def main():
    parser = argparse.ArgumentParser(description="Run system tests")
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    tester = SystemTest()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
