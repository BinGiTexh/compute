# Models Directory

This directory contains the trained models used by the video processing pipeline. Models can be downloaded from Roboflow or other sources.

## Model Structure

Each model should be organized in its own subdirectory with the following structure:

```
models/
├── model_name/
│   ├── model.pt          # PyTorch model file
│   ├── config.yaml       # Model configuration
│   └── metadata.json     # Model metadata (classes, version, etc.)
```

## Supported Models

Currently supported models:
- Roboflow YOLO models (fish-scuba-project/2)

## Adding New Models

1. Create a new directory for your model
2. Add model files following the structure above
3. Update the configuration in `configs/default_config.yaml`
4. Test the model using the test scripts

## Model Download

To download models from Roboflow:

```bash
export ROBOFLOW_API_KEY=your_key_here
python scripts/download_model.py --model-id "fish-scuba-project/2"
```

## Version Control

Model files should not be committed to Git. They are downloaded during deployment.
