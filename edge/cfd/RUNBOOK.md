# CFD Marine Pipeline v2 — Runbook

## Overview

Automated fish encounter counting on underwater transect video, calibrated
against Benny's 27-year diver survey ground truth. Runs on Jetson AGX Orin
64GB with GPU-accelerated inference.

**Pipeline strategy** (per Octavio/head ecologist):
1. Extract frames at 1/5s (not every frame)
2. Run CFD fast pass to flag fish-present frames
3. Apply skip window + ecological cap — deduplicate to unique encounters
4. Run DA3 depth ONLY on encounter frames
5. Output: encounter count comparable to diver survey methodology

**Calibration result** (ESPERANZA T1 20m, Oct 2025):
- Benny (diver): 17 species encounters
- AI (pipeline): 23 detection events (+35%)
- 6 extra events are likely re-sightings beyond the 10s skip window

## Prerequisites

- Jetson AGX Orin: `sshpass -p aburto ssh mza-bingi@10.1.102.97`
- Docker images on Jetson:
  - `ultralytics-cfd-gpu` — CFD fish detector (113ms/frame GPU)
  - `da3-cuda-jetson` — Depth Anything 3 + ffmpeg
- Video files on `/jetson-ssd/compute/edge/depth-anything-v3-marine/videos/`
- Ground truth: `~/Desktop/peces_2023_2025.csv` (Benny's diver survey)

## Quick Start

```bash
# SSH to Jetson
sshpass -p aburto ssh mza-bingi@10.1.102.97

# Run pipeline (default: cap=2)
cd /jetson-ssd/compute/edge/cfd
bash run_pipeline_v2.sh \
  /jetson-ssd/compute/edge/depth-anything-v3-marine/videos/20251107_ESPERANZA_T1_20m_V1_AR.mp4 \
  ESPERANZA T1 V1

# Or override the ecological cap
bash run_pipeline_v2.sh /path/to/video.mp4 ESPERANZA T1 V1 --max-per-event 3
```

## Compare Against Ground Truth

```bash
# On Mac (after scp'ing results)
python3 compare_to_official.py \
  --ai /jetson-ssd/pipeline/ESPERANZA/T1_V1/results/summary.csv \
  --official ~/Desktop/peces_2023_2025.csv \
  --reef ESPERANZA --depth 20 --transect 1 --year 2025
```

## Pipeline Stages & Timing (101 frames, 8K source)

| Stage | What | Time |
|-------|------|------|
| 1. Frame extraction | ffmpeg 0.2fps from 8K video | ~41 min |
| 2. CFD detection | YOLOv12x at imgsz=1024, GPU | ~12s (113ms/frame) |
| 3. Deduplication | Skip window + ecological cap | instant |
| 4. DA3 depth | Giant model on encounter frames only | ~8 min (23 frames) |
| 5. Report | Summary CSV + JSON | instant |
| **Total** | | **~50 min** |

## Output Files

```
/jetson-ssd/pipeline/ESPERANZA/T1_V1/
  frames/              101 extracted PNG frames
  cfd/detections/      Per-frame detection JSON
  depth/selected_frames/  Encounter frames (subset)
  depth/output/        DA3 depth maps (mini_npz)
  results/
    summary.csv        One row per event: fish_count (capped), fish_count_raw, max_conf
    detection_events.json   Full event data with bounding boxes
```

## Key Parameters

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `FPS` | 0.2 | 1 frame per 5 seconds |
| `SKIP_WINDOW` | 1 | Skip N frames after detection (= 10s gap) |
| `MAX_PER_EVENT` | 2 | Ecological cap per event (calibrated vs diver) |
| `CONF` | 0.30 | YOLO confidence threshold |
| `IMGSZ` | 1024 | Inference resolution (8K source letterboxed) |

## Docker Images

### ultralytics-cfd-gpu (current)

Built on `dustynv/l4t-pytorch:r36.2.0`. PyTorch 2.2 + CUDA 12.2 compatible
with L4T r35.2.1 driver on the Orin.

```bash
cd /jetson-ssd/compute/edge/cfd
docker build -f Dockerfile.ultralytics-cfd-gpu -t ultralytics-cfd-gpu .
```

Critical build notes:
- Must set `PIP_INDEX_URL=https://pypi.org/simple/` (base image's jetson index is offline)
- Must pin `numpy<2` (PyTorch 2.2 incompatible with numpy 2.x)

### da3-cuda-jetson

Same base image. Contains DA3 model (`DA3NESTED-GIANT-LARGE-1.1`, 6.76GB)
and ffmpeg. Used for both frame extraction (via `--entrypoint ffmpeg`) and
depth inference.

## Deploying Updates

Source of truth is this repo (`mcam10/turing-pi-homelab`, `cfd/` directory).
Deploy to Jetson with scp:

```bash
sshpass -p aburto scp cfd/*.py cfd/*.sh cfd/Dockerfile.* \
  mza-bingi@10.1.102.97:/jetson-ssd/compute/edge/cfd/
```

## Known Issues

- Frame extraction is slow (~41 min for 8K) — bottlenecked by ffmpeg decode, not GPU
- Chromis at distance (<30px in 8K source, <4px at inference) are undetectable
- Skip window doesn't catch fish that leave and re-enter frame after >10s
- `BinGiTexh/compute.git` on the Jetson is a legacy repo; do not use it as source of truth

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 12s/frame inference | CPU fallback | Use `ultralytics-cfd-gpu`, not `ultralytics-cfd` |
| `RuntimeError: Numpy is not available` | numpy 2.x installed | Rebuild with `numpy<2` pinned |
| CUDA device not found | Wrong base image | Must use `dustynv/l4t-pytorch:r36.2.0` |
| Stage 5 syntax error | Backslash in heredoc f-string | Fixed in current version |
