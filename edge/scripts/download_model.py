#!/usr/bin/env python3

import argparse
import json
import os
import yaml
from pathlib import Path
from inference_sdk import InferenceHTTPClient

class ModelDownloader:
    def __init__(self, api_key: str):
        self.client = InferenceHTTPClient(
            api_key=api_key
        )
        self.models_dir = Path(__file__).parent.parent / 'models'
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def download_model(self, model_id: str) -> None:
        """Download model from Roboflow."""
        try:
            print(f"Downloading model: {model_id}")
            
            # Create model directory
            model_dir = self.models_dir / model_id.replace('/', '_')
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Get model info
            model_info = self.client.get_model_info(model_id)
            
            # Save model metadata
            metadata = {
                'model_id': model_id,
                'version': model_info.get('version', 'unknown'),
                'created': model_info.get('created', ''),
                'classes': model_info.get('classes', []),
                'type': model_info.get('type', 'unknown')
            }
            
            with open(model_dir / 'metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Create model config
            config = {
                'model_id': model_id,
                'input_size': model_info.get('input_size', [640, 640]),
                'confidence_threshold': 0.1,
                'iou_threshold': 0.5,
                'classes': metadata['classes']
            }
            
            with open(model_dir / 'config.yaml', 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            print(f"Model files saved to: {model_dir}")
            print("Note: The actual model weights are downloaded at runtime by the inference SDK")
            
        except Exception as e:
            print(f"Error downloading model: {str(e)}")
            raise

    def validate_model(self, model_id: str) -> bool:
        """Validate that model files exist and are correctly formatted."""
        model_dir = self.models_dir / model_id.replace('/', '_')
        
        if not model_dir.exists():
            print(f"Model directory not found: {model_dir}")
            return False
        
        required_files = ['metadata.json', 'config.yaml']
        for file in required_files:
            if not (model_dir / file).exists():
                print(f"Missing required file: {file}")
                return False
        
        try:
            # Validate metadata
            with open(model_dir / 'metadata.json') as f:
                metadata = json.load(f)
                if 'model_id' not in metadata or 'classes' not in metadata:
                    print("Invalid metadata.json format")
                    return False
            
            # Validate config
            with open(model_dir / 'config.yaml') as f:
                config = yaml.safe_load(f)
                if 'model_id' not in config or 'classes' not in config:
                    print("Invalid config.yaml format")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error validating model files: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Download model from Roboflow")
    parser.add_argument('--model-id', required=True, help='Roboflow model ID (e.g., "fish-scuba-project/2")')
    args = parser.parse_args()
    
    api_key = os.environ.get('ROBOFLOW_API_KEY')
    if not api_key:
        raise ValueError("ROBOFLOW_API_KEY environment variable not set")
    
    downloader = ModelDownloader(api_key)
    downloader.download_model(args.model_id)
    
    if downloader.validate_model(args.model_id):
        print("Model download and validation successful")
    else:
        print("Model validation failed")

if __name__ == "__main__":
    main()
