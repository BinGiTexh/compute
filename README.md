# Marine Science Video Processing Pipeline

A modular video processing pipeline designed for marine science applications, optimized for edge computing on Jetson devices. This pipeline provides automated object detection and analysis capabilities for underwater video footage.

## Features

- Real-time object detection using Roboflow models
- System resource monitoring and performance analysis
- Automated batch processing via GitHub Actions
- Interactive analysis through JupyterLab
- Comprehensive result export (JSON, CSV)
- Docker-based deployment

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│   JupyterLab    │     │ Inference Server │     │  Result Export │
│  (Interactive)  │────▶│    (GPU/CPU)     │────▶│    (JSON/CSV)  │
└─────────────────┘     └──────────────────┘     └────────────────┘
        │                        │                        │
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Shared Storage                            │
│  - Input Videos                                                 │
│  - Trained Models                                               │
│  - Processing Results                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. Set up your Roboflow API key:
   ```bash
   export ROBOFLOW_API_KEY=your_key_here
   ```

3. Run the setup script:
   ```bash
   cd edge
   ./setup.sh
   ```

4. Access JupyterLab at http://localhost:8888

## Directory Structure

```
.
├── edge/                  # Edge computing components
│   ├── configs/           # Configuration files
│   ├── scripts/           # Processing scripts
│   ├── notebooks/         # Jupyter notebooks
│   ├── docker/            # Docker configurations
│   ├── models/            # Model storage
│   ├── output/            # Processing results
│   └── tests/             # Test files
├── cloud/                 # Cloud integration components
└── .github/               # GitHub Actions workflows
```

## Configuration

Edit `edge/configs/default_config.yaml` to modify:
- Input/output paths
- Model parameters
- Processing settings
- System requirements

## Usage

### Local Development

1. Start the services:
   ```bash
   cd edge
   docker compose up -d
   ```

2. Process a video:
   ```bash
   python scripts/process_video.py \
     --config configs/default_config.yaml \
     --video path/to/video.mp4
   ```

3. Export results:
   ```bash
   python scripts/export_results.py \
     --input output/results.json \
     --output-dir output/
   ```

### GitHub Actions

1. Push changes to trigger automatic processing
2. Use workflow_dispatch to process specific videos
3. Access results in GitHub Artifacts

## Development

### Prerequisites

- NVIDIA Jetson device or compatible hardware
- Docker and Docker Compose
- NVIDIA Container Runtime
- Python 3.8+
- Git

### Setting Up Development Environment

1. Install dependencies:
   ```bash
   pip install -r edge/docker/jupyterlab/requirements.txt
   ```

2. Download test model:
   ```bash
   python edge/scripts/download_model.py --model-id "fish-scuba-project/2"
   ```

3. Run tests:
   ```bash
   cd edge/tests
   ./run_tests.sh
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and feature requests, please use the GitHub issue tracker.
