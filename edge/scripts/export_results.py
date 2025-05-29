#!/usr/bin/env python3

import argparse
import json
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any

class ResultsExporter:
    def __init__(self, input_path: str, output_dir: str):
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def load_results(self) -> Dict[str, Any]:
        """Load results from JSON file."""
        try:
            with open(self.input_path) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading results: {str(e)}")
            raise

    def export_csv(self, results: Dict[str, Any]) -> None:
        """Export frame results to CSV format."""
        try:
            # Extract frame-level data
            frames_data = []
            for frame in results['frame_results']:
                frame_base = {
                    'frame_number': frame['frame_number'],
                    'timestamp': frame['timestamp'],
                    'cpu_percent': frame['system_stats']['cpu_percent'],
                    'memory_percent': frame['system_stats']['memory_percent'],
                    'detection_count': len(frame['predictions'])
                }
                
                # Add individual detections
                if frame['predictions']:
                    for i, pred in enumerate(frame['predictions']):
                        frame_data = frame_base.copy()
                        frame_data.update({
                            'detection_index': i,
                            'class': pred['class'],
                            'confidence': pred['confidence'],
                            'x': pred['x'],
                            'y': pred['y'],
                            'width': pred['width'],
                            'height': pred['height']
                        })
                        frames_data.append(frame_data)
                else:
                    frame_base.update({
                        'detection_index': None,
                        'class': None,
                        'confidence': None,
                        'x': None,
                        'y': None,
                        'width': None,
                        'height': None
                    })
                    frames_data.append(frame_base)
            
            # Convert to DataFrame and save
            df = pd.DataFrame(frames_data)
            output_path = self.output_dir / f"{self.input_path.stem}_detections.csv"
            df.to_csv(output_path, index=False)
            self.logger.info(f"Exported CSV to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting CSV: {str(e)}")
            raise

    def export_summary(self, results: Dict[str, Any]) -> None:
        """Export processing summary."""
        try:
            summary = {
                'video_info': results['video_info'],
                'processing_info': results['processing_info'],
                'statistics': {
                    'total_frames': len(results['frame_results']),
                    'total_detections': sum(len(f['predictions']) for f in results['frame_results']),
                    'avg_cpu_usage': sum(f['system_stats']['cpu_percent'] for f in results['frame_results']) / len(results['frame_results']),
                    'avg_memory_usage': sum(f['system_stats']['memory_percent'] for f in results['frame_results']) / len(results['frame_results']),
                    'detection_by_class': self._count_detections_by_class(results['frame_results'])
                }
            }
            
            output_path = self.output_dir / f"{self.input_path.stem}_summary.json"
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2)
            self.logger.info(f"Exported summary to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting summary: {str(e)}")
            raise

    def _count_detections_by_class(self, frame_results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count total detections for each class."""
        class_counts = {}
        for frame in frame_results:
            for pred in frame['predictions']:
                class_name = pred['class']
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
        return class_counts

    def export_all(self) -> None:
        """Export results in all formats."""
        results = self.load_results()
        self.export_csv(results)
        self.export_summary(results)
        self.logger.info("Export complete")

def main():
    parser = argparse.ArgumentParser(description="Export processing results in various formats")
    parser.add_argument('--input', required=True, help='Path to input JSON results file')
    parser.add_argument('--output-dir', required=True, help='Directory for output files')
    args = parser.parse_args()
    
    exporter = ResultsExporter(args.input, args.output_dir)
    exporter.export_all()

if __name__ == "__main__":
    main()
