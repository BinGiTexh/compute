#!/usr/bin/env python3

import argparse
import yaml
import cv2
import json
import logging
import os
import psutil
from datetime import datetime
from pathlib import Path
from inference_sdk import InferenceHTTPClient
from typing import Dict, Any

class VideoProcessor:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config['system']['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize inference client
        self.client = InferenceHTTPClient(
            api_url=self.config['inference']['api_url'],
            api_key=os.environ.get('ROBOFLOW_API_KEY')
        )
        
        # Create output directory
        os.makedirs(self.config['system']['temp_directory'], exist_ok=True)
        os.makedirs(self.config['video']['output_path'], exist_ok=True)

    def check_system_resources(self) -> bool:
        """Check if system meets minimum requirements."""
        memory_gb = psutil.virtual_memory().available / (1024**3)
        cpu_cores = psutil.cpu_count()
        
        if memory_gb < self.config['system']['min_memory_gb']:
            self.logger.error(f"Insufficient memory: {memory_gb:.1f}GB available")
            return False
        
        if cpu_cores < self.config['system']['min_cpu_cores']:
            self.logger.error(f"Insufficient CPU cores: {cpu_cores} available")
            return False
        
        return True

    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        return {
            'timestamp': datetime.now().strftime(self.config['processing']['timestamp_format']),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'available_memory_gb': psutil.virtual_memory().available / (1024**3)
        }

    def process_frame(self, frame: np.ndarray, frame_number: int) -> Dict[str, Any]:
        """Process a single frame."""
        try:
            # Get system stats
            stats = self.get_system_stats()
            
            # Run inference
            result = self.client.infer(
                frame,
                model_id=self.config['inference']['model_id']
            )
            
            # Filter predictions by confidence
            predictions = [
                pred for pred in result.get('predictions', [])
                if pred.get('confidence', 0) > self.config['inference']['confidence_threshold']
            ]
            
            # Prepare frame result
            frame_result = {
                'frame_number': frame_number,
                'timestamp': stats['timestamp'],
                'predictions': predictions,
                'system_stats': stats
            }
            
            # Draw overlay if enabled
            if any(self.config['processing']['overlay'].values()):
                self.draw_overlay(frame, frame_result)
            
            return frame_result
            
        except Exception as e:
            self.logger.error(f"Error processing frame {frame_number}: {str(e)}")
            return None

    def draw_overlay(self, frame: np.ndarray, frame_result: Dict[str, Any]) -> None:
        """Draw overlay information on frame."""
        overlay = self.config['processing']['overlay']
        h, w = frame.shape[:2]
        
        if overlay['show_system_stats']:
            stats = frame_result['system_stats']
            cv2.putText(
                frame,
                f"CPU: {stats['cpu_percent']}% | MEM: {stats['memory_percent']}%",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
        
        if overlay['show_detections']:
            for pred in frame_result['predictions']:
                self.draw_prediction(frame, pred)

    def draw_prediction(self, frame: np.ndarray, prediction: Dict[str, Any]) -> None:
        """Draw a single prediction on the frame."""
        h, w = frame.shape[:2]
        x = prediction.get('x', 0.5)
        y = prediction.get('y', 0.5)
        width = prediction.get('width', 0)
        height = prediction.get('height', 0)
        
        x1 = int((x - width/2) * w)
        y1 = int((y - height/2) * h)
        x2 = int((x + width/2) * w)
        y2 = int((y + height/2) * h)
        
        confidence = prediction.get('confidence', 0)
        class_name = prediction.get('class', 'unknown')
        
        color = (0, 255, 0) if confidence > 0.7 else (0, 255, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            f"{class_name} {confidence:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )

    def process_video(self, video_path: str) -> Dict[str, Any]:
        """Process entire video file."""
        if not self.check_system_resources():
            raise RuntimeError("System requirements not met")
        
        self.logger.info(f"Processing video: {video_path}")
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Prepare results
        results = {
            'video_info': {
                'path': video_path,
                'fps': fps,
                'frame_count': frame_count,
                'resolution': f"{width}x{height}",
                'start_time': datetime.now().isoformat()
            },
            'processing_info': {
                'model_id': self.config['inference']['model_id'],
                'confidence_threshold': self.config['inference']['confidence_threshold']
            },
            'frame_results': []
        }
        
        try:
            frame_number = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_result = self.process_frame(frame, frame_number)
                if frame_result:
                    results['frame_results'].append(frame_result)
                
                frame_number += 1
                
                if frame_number % 100 == 0:
                    self.logger.info(f"Processed {frame_number}/{frame_count} frames")
                
        except Exception as e:
            self.logger.error(f"Error during video processing: {str(e)}")
            raise
        
        finally:
            cap.release()
            results['video_info']['end_time'] = datetime.now().isoformat()
            
            # Save results
            output_base = Path(self.config['video']['output_path'])
            video_name = Path(video_path).stem
            
            if 'json' in self.config['processing']['export_format']:
                with open(output_base / f"{video_name}_results.json", 'w') as f:
                    json.dump(results, f, indent=2)
            
            self.logger.info("Processing complete")
            return results

def main():
    parser = argparse.ArgumentParser(description="Process video file with ML model")
    parser.add_argument('--config', required=True, help='Path to config file')
    parser.add_argument('--video', required=True, help='Path to video file')
    args = parser.parse_args()
    
    processor = VideoProcessor(args.config)
    processor.process_video(args.video)

if __name__ == "__main__":
    main()
