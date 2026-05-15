# Edge Compute — Marine AI Pipeline

GPU-accelerated marine video analysis on NVIDIA Jetson AGX Orin 64GB. Fish detection, monocular depth estimation, and automated encounter counting calibrated against professional diver surveys.

## Active Components

### CFD Fish Detection Pipeline (`cfd/`)

End-to-end fish encounter counting from underwater transect video.

- **Container:** `ultralytics-cfd-gpu` (YOLOv12x, 113ms/frame on Orin)
- **Pipeline:** `run_pipeline_v2.sh` — extract → detect → deduplicate → depth → report
- **Validation:** Calibrated against 27-year diver survey (ESPERANZA T1: 23 AI events vs 17 diver encounters)
- **Runbook:** [`cfd/RUNBOOK.md`](cfd/RUNBOOK.md)

```bash
cd cfd
bash run_pipeline_v2.sh /jetson-ssd/videos/T1.mp4 ESPERANZA T1 V1
```

### Depth Anything V3 (`depth-anything-v3-marine/`)

Monocular depth estimation for marine video. Used by the CFD pipeline for 3D depth maps of fish encounter frames.

- **Container:** `da3-cuda-jetson` (DA3NESTED-GIANT-LARGE-1.1, 6.76GB model)
- **Base:** `dustynv/l4t-pytorch:r36.2.0` (PyTorch 2.2 + CUDA 12.2)
- **Dockerfiles:** `Dockerfile.da3-cli` (production), `Dockerfile.da3-complete` (with extras)

```bash
docker run --rm --runtime nvidia -v /jetson-ssd:/jetson-ssd \
  da3-cuda-jetson images /path/to/frames \
  --model-dir depth-anything/DA3NESTED-GIANT-LARGE-1.1 \
  --export-dir /path/to/output --export-format mini_npz
```

### Supporting Tools

| Component | Purpose |
|-----------|---------|
| `yolo.py` | Basic YOLO inference script |
| `yolo_improved_inference.py` | YOLO with argparse and result export |
| `coralscapes_jetson.py` | Coral reef segmentation and classification |
| `nanoowl_inference.py` | Open-vocabulary detection (NVIDIA NanoOWL) |
| `monitoring.py` | GPU/system resource monitoring |
| `base_config.py` | Shared configuration for edge workloads |
| `notebooks/` | Jupyter notebooks for exploration and diagnostics |

## Hardware

- **NVIDIA Jetson AGX Orin 64GB** (L4T r35.2.1, CUDA 11.4 driver)
- **Storage:** `/jetson-ssd/` (NVMe, pipeline data and containers)
- **Access:** `sshpass -p aburto ssh mza-bingi@10.1.102.97`

## Docker Images

| Image | Base | Purpose | Perf |
|-------|------|---------|------|
| `ultralytics-cfd-gpu` | `dustynv/l4t-pytorch:r36.2.0` | Fish detection (YOLOv12x) | 113ms/frame |
| `da3-cuda-jetson` | `dustynv/l4t-pytorch:r36.2.0` | Depth estimation + ffmpeg | 20s/frame (giant) |

Both images use the same base to avoid CUDA driver mismatch. Key constraint: must pin `numpy<2` for PyTorch 2.2 compatibility.

## Directory Structure

```
edge/
  cfd/                        Fish detection pipeline (source of truth)
  depth-anything-v3-marine/   DA3 depth estimation
  configs/                    Model and device configs
  devices/                    Device-specific setup
  docker/                     Shared Docker utilities
  docs/                       Architecture documentation
  jetson-runner/              GitHub Actions self-hosted runner
  jetson-segmentation/        Segmentation pipeline
  models/                     Model registry
  notebooks/                  Jupyter exploration notebooks
  scripts/                    Utility scripts (benchmark, export, etc.)
  tests/                      Test suite
```

## Workflow

1. Video files land on `/jetson-ssd/compute/edge/depth-anything-v3-marine/videos/`
2. Run `cfd/run_pipeline_v2.sh` for automated fish encounter counting
3. Compare results against ground truth: `cfd/compare_to_official.py`
4. Push results to S3: `aws s3 sync` to `s3://ml-ai-assets/marine-datasets/`

## Source of Truth

Code is maintained in two repos:
- **`mcam10/turing-pi-homelab`** (`cfd/` directory) — primary development
- **`BinGiTexh/compute`** (`edge/` directory) — Jetson deployment, `git pull` to update

Keep both in sync. Develop locally, push to both, pull on Jetson.
