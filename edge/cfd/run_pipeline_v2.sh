#!/bin/bash
# Optimized Marine Video Pipeline v2
# CFD-first filtering with skip-window deduplication
#
# Strategy (per Octavio/head ecologist):
#   1. Extract frames at 1/5s (not every frame)
#   2. Run CFD fast pass to flag fish-present frames
#   3. Apply skip window — same school = one detection event
#   4. Run DA3 depth ONLY on unique detection events
#   5. Output: deduplicated fish count comparable to diver survey
#
# Usage: ./run_pipeline_v2.sh <video_path> <site> <transect> <version> [--max-per-event N]
# Example: ./run_pipeline_v2.sh /jetson-ssd/videos/T1.mp4 ESPERANZA T1 V1 --max-per-event 2

set -e

VIDEO=$1
SITE=${2:-ESPERANZA}
TRANSECT=${3:-T1}
VERSION=${4:-V1}

# Ecological cap: max fish counted per unique detection event.
# Calibrated to match diver survey methodology (cap=2 → -6% vs manual
# count on ESPERANZA T1).
MAX_PER_EVENT=2

# Parse optional flags
shift 4 2>/dev/null || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --max-per-event) MAX_PER_EVENT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

PIPELINE_ROOT=/jetson-ssd/pipeline/$SITE/${TRANSECT}_${VERSION}
FRAMES_DIR=$PIPELINE_ROOT/frames
CFD_DIR=$PIPELINE_ROOT/cfd
DEPTH_DIR=$PIPELINE_ROOT/depth
RESULTS_DIR=$PIPELINE_ROOT/results

FPS=0.2  # 1 frame per 5 seconds
SKIP_WINDOW=1  # skip N frames after detection (= 5s at 0.2fps)
CONF=0.30
IMGSZ=1024

echo "=============================================="
echo "  Marine Pipeline v2 — CFD-First Filtering"
echo "=============================================="
echo "Video:       $VIDEO"
echo "Site:        $SITE / $TRANSECT / $VERSION"
echo "Output:      $PIPELINE_ROOT"
echo "Sampling:    ${FPS} fps (1 frame per 5 seconds)"
echo "Skip window: ${SKIP_WINDOW} frames (5s after detection)"
echo "Max/event:   ${MAX_PER_EVENT} fish (ecological cap)"
echo "=============================================="
echo ""

mkdir -p $FRAMES_DIR $CFD_DIR $DEPTH_DIR $RESULTS_DIR

# ─── STAGE 1: Extract frames at 1/5s ───────────────────────────────────
echo "=== STAGE 1: Frame Extraction (${FPS} fps) ==="
START=$(date +%s)

docker run --rm --runtime nvidia \
  -v /jetson-ssd:/jetson-ssd \
  --entrypoint ffmpeg \
  da3-cuda-jetson \
  -i "$VIDEO" \
  -vf "fps=$FPS" \
  -q:v 2 \
  "$FRAMES_DIR/%06d.png" \
  -y 2>/dev/null

FRAME_COUNT=$(ls $FRAMES_DIR/*.png 2>/dev/null | wc -l)
ELAPSED=$(($(date +%s) - START))
echo "  Extracted $FRAME_COUNT frames in ${ELAPSED}s"
echo ""

# ─── STAGE 2: CFD fast pass ─────────────────────────────────────────────
echo "=== STAGE 2: CFD Fish Detection (fast pass) ==="
START=$(date +%s)

docker run --rm --runtime nvidia \
  -v $PIPELINE_ROOT:/outputs \
  ultralytics-cfd-gpu \
  --frames /outputs/frames \
  --output /outputs/cfd \
  --conf $CONF \
  --imgsz $IMGSZ

ELAPSED=$(($(date +%s) - START))
echo "  CFD complete in ${ELAPSED}s"
echo ""

# ─── STAGE 3: Skip-window deduplication ─────────────────────────────────
echo "=== STAGE 3: Deduplication (skip window = ${SKIP_WINDOW} frames) ==="

python3 << PYEOF
import csv, json, shutil, os
from pathlib import Path

cfd_dir = Path("$CFD_DIR")
results_dir = Path("$RESULTS_DIR")
frames_dir = Path("$FRAMES_DIR")
depth_dir = Path("$DEPTH_DIR")
skip_window = $SKIP_WINDOW
max_per_event = $MAX_PER_EVENT

det_dir = cfd_dir / "detections"
depth_frames_dir = depth_dir / "selected_frames"
depth_frames_dir.mkdir(parents=True, exist_ok=True)

# Read per-frame fish counts
frame_files = sorted(det_dir.glob("*.json"))
events = []
last_event_idx = -999

for i, jf in enumerate(frame_files):
    with open(jf) as f:
        data = json.load(f)

    fish_count = data.get("fish_count_filtered", 0)
    if fish_count == 0:
        continue

    # Skip window: if this frame is within skip_window of last event, skip it
    if i - last_event_idx <= skip_window:
        continue

    # This is a new detection event
    last_event_idx = i
    frame_name = data["frame"]
    fish = [d for d in data["detections"] if not d["likely_diver"]]
    raw_count = len(fish)
    capped_count = min(raw_count, max_per_event)

    events.append({
        "event_id": len(events) + 1,
        "frame": frame_name,
        "frame_index": i,
        "fish_count_raw": raw_count,
        "fish_count": capped_count,
        "max_conf": max(d["confidence"] for d in fish) if fish else 0,
        "detections": fish,
    })

    # Copy this frame to depth processing queue
    src = frames_dir / frame_name
    if src.exists():
        shutil.copy2(src, depth_frames_dir / frame_name)

# Write detection events
with open(results_dir / "detection_events.json", "w") as f:
    json.dump(events, f, indent=2)

# Write deduplicated summary
total_raw = sum(e["fish_count_raw"] for e in events)
total_capped = sum(e["fish_count"] for e in events)
with open(results_dir / "summary.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "event_id", "frame", "fish_count", "fish_count_raw", "max_conf"])
    writer.writeheader()
    for e in events:
        writer.writerow({
            "event_id": e["event_id"],
            "frame": e["frame"],
            "fish_count": e["fish_count"],
            "fish_count_raw": e["fish_count_raw"],
            "max_conf": round(e["max_conf"], 4),
        })

n_total = len(frame_files)
n_with_fish = sum(1 for jf in frame_files
                  for _ in [json.load(open(jf))]
                  if _["fish_count_filtered"] > 0)
n_events = len(events)
n_depth = len(list(depth_frames_dir.glob("*.png")))

print(f"  Total frames:              {n_total}")
print(f"  Frames with fish:          {n_with_fish}")
print(f"  Unique detection events:   {n_events} (after {skip_window}-frame skip window)")
print(f"  Fish count (raw):          {total_raw}")
print(f"  Fish count (capped at {max_per_event}):  {total_capped}")
print(f"  Frames queued for DA3:     {n_depth}")
print(f"  Reduction ratio:           {n_total}→{n_depth} ({100*(1-n_depth/max(n_total,1)):.0f}% saved)")
PYEOF

echo ""

# ─── STAGE 4: DA3 depth on selected frames only ────────────────────────
DEPTH_FRAME_COUNT=$(ls $DEPTH_DIR/selected_frames/*.png 2>/dev/null | wc -l)

if [ "$DEPTH_FRAME_COUNT" -gt 0 ]; then
    echo "=== STAGE 4: DA3 Depth (${DEPTH_FRAME_COUNT} frames only) ==="
    START=$(date +%s)

    docker run --rm --runtime nvidia \
      -v /jetson-ssd:/jetson-ssd \
      da3-cuda-jetson \
      images "$DEPTH_DIR/selected_frames" \
      --model-dir depth-anything/DA3NESTED-GIANT-LARGE-1.1 \
      --export-dir "$DEPTH_DIR/output" \
      --export-format mini_npz \
      --auto-cleanup

    ELAPSED=$(($(date +%s) - START))
    echo "  DA3 complete in ${ELAPSED}s"
else
    echo "=== STAGE 4: SKIPPED (no fish-bearing frames) ==="
fi

echo ""

# ─── STAGE 5: Final report ──────────────────────────────────────────────
echo "=== STAGE 5: Final Report ==="

python3 << PYEOF
import json, csv
from pathlib import Path

results_dir = Path("$RESULTS_DIR")
events_file = results_dir / "detection_events.json"
max_per_event = $MAX_PER_EVENT

with open(events_file) as f:
    events = json.load(f)

total_raw = sum(e["fish_count_raw"] for e in events)
total_capped = sum(e["fish_count"] for e in events)
n_events = len(events)

print("")
print("  ┌─────────────────────────────────────────────────┐")
print("  │  PIPELINE v2 RESULTS                            │")
print("  ├─────────────────────────────────────────────────┤")
print(f"  │  Detection events:         {n_events:<20}│")
print(f"  │  Fish count (raw):         {total_raw:<20}│")
print(f"  │  Fish count (capped):      {total_capped:<20}│")
print(f"  │  Ecological cap:           {max_per_event} per event{'':<13}│")
print(f"  │  Mean fish/event (capped): {total_capped/max(n_events,1):<20.1f}│")
print("  └─────────────────────────────────────────────────┘")
print("")
print("  Compare with Benny's diver count using:")
print("    python3 compare_to_official.py \\\\")
print("      --ai $RESULTS_DIR/summary.csv \\\\")
print("      --official <benny_csv>")
print("")
PYEOF

echo "=== PIPELINE v2 COMPLETE ==="
echo "Results: $RESULTS_DIR/"
echo "  - detection_events.json  (full event data)"
echo "  - summary.csv            (deduplicated counts)"
echo "  - $DEPTH_DIR/output/     (3D depth for fish frames)"
