#!/usr/bin/env python3
"""Fuse CFD fish detections with DA3 depth maps."""
import argparse, json, csv, os
from pathlib import Path
import numpy as np
import cv2


def depth_to_color(depth_m, d_min=0.5, d_max=10.0):
    """Map depth to BGR color: green(shallow) -> yellow(mid) -> red(deep)."""
    t = np.clip((depth_m - d_min) / (d_max - d_min), 0, 1)
    if t < 0.5:
        # green -> yellow
        r, g, b = int(255 * t * 2), 255, 0
    else:
        # yellow -> red
        r, g, b = 255, int(255 * (1 - (t - 0.5) * 2)), 0
    return (b, g, r)  # BGR


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--frames", required=True)
    p.add_argument("--depth", required=True)
    p.add_argument("--cfd", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--site", default="SITE")
    p.add_argument("--transect", default="T1")
    return p.parse_args()


def main():
    args = parse_args()
    frames_dir = Path(args.frames)
    depth_dir = Path(args.depth)
    cfd_dir = Path(args.cfd)
    out_dir = Path(args.output)
    fused_dir = out_dir / "fused_annotated"
    fused_dir.mkdir(parents=True, exist_ok=True)

    det_files = sorted((cfd_dir / "detections").glob("*.json"))
    if not det_files:
        print("No detection JSONs found"); return

    rows = []
    all_depths = []
    best_frame, best_count = None, 0

    for det_path in det_files:
        stem = det_path.stem
        with open(det_path) as f:
            det = json.load(f)

        depth_path = depth_dir / f"{stem}.npy"
        if not depth_path.exists():
            continue

        depth = np.load(str(depth_path))
        dh, dw = depth.shape
        frame_path = frames_dir / det["frame"]
        img = cv2.imread(str(frame_path))
        if img is None:
            continue
        fh, fw = img.shape[:2]
        sy, sx = dh / fh, dw / fw

        fish_dets = [d for d in det["detections"] if not d["likely_diver"]]
        for d in fish_dets:
            cx, cy = d["center"]
            dx, dy = int(cx * sx), int(cy * sy)
            dx, dy = min(dx, dw-1), min(dy, dh-1)
            z = float(depth[dy, dx])
            d["depth_m"] = round(z, 3)
            all_depths.append(z)

            color = depth_to_color(z)
            x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
            cv2.rectangle(img, (x1,y1), (x2,y2), color, 2)
            lbl = f"{d['confidence']:.2f} {z:.1f}m"
            cv2.putText(img, lbl, (x1, y1-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # diver boxes in orange
        for d in det["detections"]:
            if d["likely_diver"]:
                x1,y1,x2,y2 = [int(v) for v in d["bbox"]]
                cv2.rectangle(img, (x1,y1),(x2,y2), (0,165,255), 2)

        n_fish = len(fish_dets)
        txt = f"{stem} | Fish:{n_fish}"
        cv2.putText(img, txt, (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)

        scale = 1920/fw if fw > 1920 else 1.0
        if scale < 1.0:
            img = cv2.resize(img, (1920, int(fh*scale)))
        cv2.imwrite(str(fused_dir/f"{stem}.jpg"), img,
                    [cv2.IMWRITE_JPEG_QUALITY, 85])

        fish_depths = [d["depth_m"] for d in fish_dets if "depth_m" in d]
        mean_d = np.mean(fish_depths) if fish_depths else 0
        rows.append({
            "frame": det["frame"], "fish_count": n_fish,
            "mean_depth_m": round(mean_d, 3),
            "min_depth_m": round(min(fish_depths), 3) if fish_depths else 0,
            "max_depth_m": round(max(fish_depths), 3) if fish_depths else 0,
        })
        if n_fish > best_count:
            best_count = n_fish
            best_frame = stem

    # CSV
    with open(out_dir/"fused_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "frame","fish_count","mean_depth_m","min_depth_m","max_depth_m"])
        w.writeheader(); w.writerows(rows)

    # Best frame highlight
    if best_frame:
        src = fused_dir / f"{best_frame}.jpg"
        if src.exists():
            import shutil
            shutil.copy(str(src), str(out_dir/"best_frame_highlight.jpg"))

    # Filmstrip: top 5 frames by fish count
    top5 = sorted(rows, key=lambda r: r["fish_count"], reverse=True)[:5]
    strips = []
    for r in top5:
        stem = Path(r["frame"]).stem
        p = fused_dir / f"{stem}.jpg"
        if p.exists():
            im = cv2.imread(str(p))
            im = cv2.resize(im, (384, 216))
            strips.append(im)
    if strips:
        filmstrip = np.hstack(strips)
        cv2.imwrite(str(out_dir/"filmstrip.jpg"), filmstrip,
                    [cv2.IMWRITE_JPEG_QUALITY, 90])

    # Console report
    ad = np.array(all_depths) if all_depths else np.array([0])
    print(f"\n=== FUSION RESULTS: {args.site} {args.transect} ===")
    print(f"Frames processed: {len(rows)}")
    print(f"Total fish (filtered): {sum(r['fish_count'] for r in rows)}")
    print(f"Depth range: {ad.min():.2f}m - {ad.max():.2f}m")
    print(f"Depth range (5th-95th pct): {np.percentile(ad,5):.2f}m - {np.percentile(ad,95):.2f}m")
    print(f"Mean fish depth: {ad.mean():.2f}m")
    print(f"Median fish depth: {np.median(ad):.2f}m")
    print(f"Best frame: {best_frame} ({best_count} fish)")
    print(f"Top 5: {[(r['frame'], r['fish_count']) for r in top5]}")
    print(f"Output: {out_dir}")
    print("=" * 40)


if __name__ == "__main__":
    main()
