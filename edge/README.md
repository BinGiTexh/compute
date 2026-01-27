# JupyterLab with YOLO, Roboflow Integration, and Marine AI Analysis

This project provides a comprehensive dockerized environment for computer vision and marine AI research, specifically configured for the fish-scuba-project and marine video analysis.

## 🚀 New: Depth-Anything-V3 Marine Analysis

### **TensorRT-Optimized Marine Depth Estimation**
We have successfully implemented **Depth-Anything-V3** with TensorRT optimization for marine video analysis:

- 📁 **Implementation**: `depth-anything-v3-marine/`
- 🐢 **Tested**: 5-minute turtle video analysis (113 frames → 339 outputs)
- ⚡ **Performance**: 0.27s/frame with GPU acceleration (3.7 FPS)
- 🔬 **Interactive**: JupyterLab visualization environment
- 🌊 **Marine-optimized**: Blue channel dominance detection

**Quick Start:**
```bash
cd depth-anything-v3-marine
./run_turtle_analysis.sh your_marine_video.mp4
```

[**→ Full Documentation**](depth-anything-v3-marine/README.md)

---

## 🔧 YOLO and Roboflow Integration

This project provides a dockerized JupyterLab environment with YOLO and Roboflow integration.

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

## 🌊 Available Marine AI Components

### 1. Depth-Anything-V3 Marine Analysis (`depth-anything-v3-marine/`)
- **TensorRT-optimized depth estimation** for marine environments
- **Interactive visualization** with JupyterLab notebooks
- **Production-ready pipeline** tested on turtle video analysis
- **Marine environment detection** using blue channel analysis

### 2. YOLO Object Detection (`yolo.py`, `yolo_improved_inference.py`)
- **Roboflow integration** for custom marine datasets
- **Real-time inference** with GPU acceleration
- **Bounding box visualization** and export

### 3. Coralscapes Analysis (`coralscapes_jetson.py`)
- **Coral reef analysis** and classification
- **Micromamba environment** for dependency management
- **Overlay visualization** with configurable alpha blending

### 4. NanoOWL Inference (`nanoowl_inference.py`)
- **Open-vocabulary object detection** for marine life
- **Natural language queries** for species detection
- **Lightweight inference** optimized for edge devices

## 🔬 Research Applications

### Marine Biology
- **Turtle behavior analysis** with depth profiling
- **Fish population surveys** with automated detection
- **Coral reef health monitoring** and classification
- **3D habitat reconstruction** from depth maps

### Conservation
- **Biodiversity assessments** using AI-powered species identification
- **Habitat quality analysis** through depth and visual features
- **Behavioral pattern recognition** for wildlife monitoring
- **Impact assessment** of environmental changes

## 📊 Performance Benchmarks

| Component | Processing Speed | GPU Utilization | Accuracy |
|-----------|-----------------|-----------------|-----------|
| Depth-Anything-V3 | 0.27s/frame (3.7 FPS) | ~2GB VRAM | High depth quality |
| YOLO Detection | Real-time | Variable | Model-dependent |
| Coralscapes | Batch processing | Optimized | Coral classification |

## 🤝 Contributing

This is part of the **BinGiTech Compute Edge** platform for marine AI research:

1. Fork the repository
2. Create feature branch for your marine AI component
3. Test on marine datasets
4. Submit pull request with performance benchmarks

---

**🔬 Built for Marine Conservation Research**  
**⚡ Optimized for NVIDIA Jetson AGX Orin**  
**🌊 Ready for Underwater AI Applications**
