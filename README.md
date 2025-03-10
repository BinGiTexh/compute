This repository provides tools, configurations, and examples for deploying machine learning and AI workloads across diverse compute platforms - from cloud-based AWS resources to edge-based NVIDIA Jetson devices.

Overview
This project demonstrates end-to-end ML/AI workflows spanning centralized cloud infrastructure and distributed edge devices. It includes optimized configurations for model training in the cloud and efficient inference deployment at the edge.

Cloud Training (AWS)
Supported Instance Types
g6e.xlarge - 1GPU

Edge Inference (NVIDIA Jetson & Rasberry Pi's coming soon)
Supported Devices
Jetson Nano (4GB) JP4
Jetson Orin Nano Super (8GB) JP6
Jetson Orin Nano (4GB) JP6

Model Pipeline
The repository implements a complete workflow:

Train models on AWS cloud instances
Convert and optimize for edge deployment
Deploy to Jetson devices with performance monitoring integrated with Github through Github Actions. Each edge device is used an internal runner for experimentation, closer to codebase and enhances colloboration.
Capture analytics and feedback for retraining

