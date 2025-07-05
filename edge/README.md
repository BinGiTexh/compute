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


For your NVIDIA Jetson AGX Orin 64GB, here are the best open-source models that can give you Claude-like performance when running locally:
🚀 Top Recommendations
1. Llama 3.1 8B Instruct (Recommended)

Performance: Excellent reasoning and instruction following
Memory: ~16GB VRAM (with quantization)
Strengths: Strong coding, analysis, and conversational abilities
Implementation: Use llama.cpp or Ollama for efficient inference

2. Qwen2.5 14B Instruct

Performance: Very strong coding and reasoning capabilities
Memory: ~28GB VRAM (may need aggressive quantization)
Strengths: Excellent at technical tasks, multilingual
Note: Might be tight on memory but worth trying with 4-bit quantization

3. CodeLlama 13B Instruct

Performance: Specialized for coding tasks
Memory: ~26GB VRAM (with quantization)
Strengths: Exceptional at code generation and debugging
Best for: If you're primarily doing development work

🛠 Recommended Setup Stack
Inference Engines
bash# Option 1: Ollama (Easiest)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b

# Option 2: llama.cpp (More control)
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make LLAMA_CUBLAS=1
Quantization for Memory Efficiency

4-bit (Q4_K_M): ~50% memory reduction, minimal quality loss
5-bit (Q5_K_M): ~40% memory reduction, better quality
8-bit (Q8_0): ~25% memory reduction, near-original quality

💡 Optimization Tips for Jetson AGX Orin
Memory Management
bash# Increase swap space
sudo fallocate -l 32G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
CUDA Optimization

Enable CUDA acceleration in inference engines
Use mixed precision (FP16/INT8) for better performance
Monitor GPU memory usage with nvidia-smi

Power Mode
bash# Set maximum performance mode
sudo nvpmodel -m 0
sudo jetson_clocks
📊 Expected Performance
ModelSizeMemory UsageTokens/secQuality vs ClaudeLlama 3.1 8B8B~16GB15-2575-80%Qwen2.5 14B14B~28GB8-1580-85%CodeLlama 13B13B~26GB10-1870-75% (coding)
🔧 Quick Start Commands
Using Ollama
bash# Install and run Llama 3.1 8B
ollama pull llama3.1:8b
ollama run llama3.1:8b

# For coding tasks
ollama pull codellama:13b-instruct
ollama run codellama:13b-instruct
Using llama.cpp
bash# Download quantized model
wget https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf

# Run with CUDA
./main -m Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf -n 512 -gpu-layers 32
🎯 Best Choice for Your Use Case
Given your 64GB system RAM and the Jetson's capabilities, I'd recommend starting with Llama 3.1 8B Instruct using Ollama. It offers:

Excellent balance of performance and resource usage
Strong general capabilities similar to Claude
Easy setup and management
Good community support and regular updates
Reliable performance on ARM-based systems

You can always experiment with larger models like Qwen2.5 14B if you find the 8B model insufficient for your needs. The 64GB RAM gives you good flexibility for model swapping and experimentation.
