# JupyterLab with YOLO and Roboflow Integration

This project provides a dockerized JupyterLab environment with YOLO and Roboflow integration, specifically configured for the fish-scuba-project.

## Prerequisites

1. Docker installed on your system
2. NVIDIA GPU with appropriate drivers
3. NVIDIA Container Toolkit installed
4. Roboflow API key

### Installing NVIDIA Container Toolkit

```bash
curl -s -L https://nvidia.github.io/nvidia-container-runtime/gpgkey | \
    sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## Building and Running

### Using Docker Compose (Recommended)

1. Export your Roboflow API key:
   ```bash
   export ROBOFLOW_API_KEY=your_api_key
   ```

2. Build and start the container:
   ```bash
   docker-compose up --build
   ```

### Using Docker Directly

1. Build the image:
   ```bash
   docker build -t jupyterlab-yolo .
   ```

2. Run the container:
   ```bash
   docker run --gpus all -p 8888:8888 \
     -v $(pwd)/notebooks:/workspace/notebooks \
     -v $(pwd)/data:/workspace/data \
     -e ROBOFLOW_API_KEY=your_api_key \
     jupyterlab-yolo
   ```

## Accessing JupyterLab

1. Once the container is running, open your browser and navigate to:
   ```
   http://localhost:8888
   ```

2. Enter the token specified in the docker-compose.yml file (default: "your_secure_token")

## Using the YOLO Model

1. Open the provided `notebooks/yolo_demo.ipynb` notebook
2. The notebook includes examples of:
   - Loading the Roboflow model
   - Running inference on images
   - Visualizing results

## Data Persistence

- Notebooks are persisted in the `./notebooks` directory
- Data files are persisted in the `./data` directory
- Both directories are mounted as volumes in the container

## Security Notes

1. Change the default JUPYTER_TOKEN in docker-compose.yml before deploying
2. Never commit your Roboflow API key to version control
3. Use environment variables for sensitive information

## Troubleshooting

1. If GPU is not detected, ensure nvidia-container-toolkit is properly installed
2. For authentication issues, verify your Roboflow API key is correctly set
3. For permission issues with mounted volumes, ensure proper directory permissions


## Running coralscapes on Jetson AGX
"${SHELL}" <(curl -L https://micro.mamba.pm/install.sh)

micromamba env create -f environment.yml
micromamba activate coralscapes
eval "$(micromamba shell hook --shell bash)"
micromamba activate coralscapes

python coralscapes_jetson.py  --input_dir ocean-images --output_dir outputs --save_overlay --overlay_alpha 0.5
