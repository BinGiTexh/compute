#!/usr/bin/env python3
"""Community Fish Detector (CFD) pipeline - Stage 2."""
import argparse
import json
import csv
import os
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


def parse_args():
    p = argparse.ArgumentParser(description="CFD fish detection")
    p.add_argument("--frames", default="/outputs/frames")
    p.add_argument("--output", default="/outputs/cfd")
    p.add_argument("--model", default="/app/cfd-yolov12x-1.00.pt")
    p.add_argument("--conf", type=float, default=0.3)
    p.add_argument("--imgsz", type=int, default=1024)
    return p.parse_args()


def main():
    args = parse_args()
    frames_dir = Path(args.frames)
    output_dir = Path(args.output)
    det_dir = output_dir / "detections"
    ann_dir = output_dir / "annotated"
    det_dir.mkdir(parents=True, exist_ok=True)
    ann_dir.mkdir(parents=True, exist_ok=True)

    pngs = sorted(frames_dir.glob("*.png"))
    if not pngs:
        print(f"No PNG files found in {frames_dir}")
        return

    print(f"Found {len(pngs)} frames in {frames_dir}")
    model = YOLO(args.model)

    results = model.predict(
        source=str(frames_dir),
        imgsz=args.imgsz,
        conf=args.conf,
        stream=True,
    )

    csv_rows = []
    total_raw = 0
    total_filtered = 0
    total_diver = 0
    zero_fish = 0
    frame_counts = []

    for result in results:
        src = Path(result.path)
        stem = src.stem
        img = cv2.imread(str(src))
        h, w = img.shape[:2]
        frame_area = h * w

        detections = []
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
            conf = float(box.conf[0].cpu())
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            bw = x2 - x1
            bh = y2 - y1
            area_pct = (bw * bh) / frame_area
            likely_diver = area_pct > 0.10 or y2 < h * 0.20
            detections.append({
                "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                "confidence": round(conf, 4),
                "center": [round(cx, 1), round(cy, 1)],
                "area_pct": round(area_pct, 5),
                "likely_diver": likely_diver,
            })

        fish = [d for d in detections if not d["likely_diver"]]
        divers = [d for d in detections if d["likely_diver"]]

        frame_json = {
            "frame": src.name,
            "fish_count": len(detections),
            "detections": detections,
            "fish_count_filtered": len(fish),
            "diver_detections": len(divers),
        }
        with open(det_dir / f"{stem}.json", "w") as f:
            json.dump(frame_json, f, indent=2)

        # Annotated image
        for d in detections:
            x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
            if d["likely_diver"]:
                color = (0, 165, 255)  # orange BGR
            else:
                color = (0, 255, 0)  # green BGR
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            label = f"{d['confidence']:.2f}"
            cv2.putText(img, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        txt = f"Frame: {stem}  Fish: {len(fish)}"
        cv2.putText(img, txt, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        scale = 1920 / w if w > 1920 else 1.0
        if scale < 1.0:
            img = cv2.resize(img, (1920, int(h * scale)))
        cv2.imwrite(str(ann_dir / f"{stem}.jpg"), img,
                    [cv2.IMWRITE_JPEG_QUALITY, 85])

        confs = [d["confidence"] for d in fish] if fish else [0]
        csv_rows.append({
            "frame": src.name,
            "fish_count_raw": len(detections),
            "fish_count_filtered": len(fish),
            "diver_detections": len(divers),
            "max_conf": round(max(confs), 4),
            "mean_conf": round(sum(confs) / len(confs), 4),
        })

        total_raw += len(detections)
        total_filtered += len(fish)
        total_diver += len(divers)
        if len(fish) == 0:
            zero_fish += 1
        frame_counts.append((src.name, len(fish)))

        print(f"  {src.name}: {len(fish)} fish, {len(divers)} diver")

    # Write CSV
    with open(output_dir / "summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "frame", "fish_count_raw", "fish_count_filtered",
            "diver_detections", "max_conf", "mean_conf"])
        writer.writeheader()
        writer.writerows(csv_rows)

    # Console report
    n = len(pngs)
    mean_fish = total_filtered / n if n else 0
    top5 = sorted(frame_counts, key=lambda x: x[1], reverse=True)[:5]
    print("\n=== CFD RESULTS ===")
    print(f"Total frames processed: {n}")
    print(f"Total fish detections (raw): {total_raw}")
    print(f"Total fish detections (filtered): {total_filtered}")
    print(f"Likely diver detections removed: {total_diver}")
    print(f"Mean fish per frame: {mean_fish:.2f}")
    print(f"Frames with 0 fish: {zero_fish}")
    print(f"Top 5 frames by fish count: {top5}")
    print("==================")


if __name__ == "__main__":
    main()
