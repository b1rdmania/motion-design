#!/usr/bin/env python3
"""Activity per frame, detected cuts and still runs for a rendered video.

It measures activity. It does not establish good pacing.

    python3 motion_strip.py video.mp4 --out review/strip [--score plan/score.json]

Writes strip.csv, strip.json and strip.png to --out.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from _common import load_json, need, probe, write_json  # noqa: E402

W, H = 160, 90          # analysis size; small is enough for activity
CUT_MIN = 0.03          # mean abs RGB diff (0..1) a cut must exceed
CUT_RATIO = 5.0         # and exceed this multiple of the local median
STILL_MAX = 0.004       # below this a frame counts as still


def read_frames(video: Path) -> tuple[np.ndarray, float]:
    need("ffmpeg")
    info = probe(video)
    if not info["ok"] or not info["video"]:
        raise SystemExit(f"cannot read video: {info.get('error', 'no video stream')}")
    fps = info["video"]["fps"]
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"scale={W}:{H},format=rgb24",
         "-f", "rawvideo", "-"],
        capture_output=True, check=True,
    )
    frames = np.frombuffer(proc.stdout, dtype=np.uint8)
    frames = frames[: (frames.size // (W * H * 3)) * W * H * 3].reshape(-1, H, W, 3).astype(np.float32) / 255.0
    return frames, fps


def analyse(frames: np.ndarray, fps: float) -> dict:
    n = len(frames)
    act = np.zeros(n, dtype=np.float32)
    if n > 1:
        act[1:] = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2, 3))
    cuts = []
    for i in range(1, n):
        lo, hi = max(1, i - 6), min(n, i + 7)
        neighbours = np.concatenate([act[lo:i], act[i + 1:hi]])
        local = float(np.median(neighbours)) if neighbours.size else 0.0
        if act[i] > CUT_MIN and act[i] > CUT_RATIO * max(local, 1e-3):
            cuts.append(i)
    still = act < STILL_MAX
    runs, start = [], None
    for i, s in enumerate(still):
        if s and start is None:
            start = i
        if (not s or i == n - 1) and start is not None:
            end = i if not s else i + 1
            if end - start >= 2:
                runs.append((start, end))
            start = None
    return {
        "fps": fps,
        "frames": n,
        "activity": act,
        "cuts": [{"frame": c, "t": round(c / fps, 3)} for c in cuts],
        "still_runs": [{"start": round(a / fps, 3), "end": round(b / fps, 3), "dur": round((b - a) / fps, 3)}
                       for a, b in runs],
    }


def draw(result: dict, score: dict | None, path: Path) -> None:
    act, fps = result["activity"], result["fps"]
    width, height, pad = 1200, 220, 20
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)
    n = max(len(act), 1)
    peak = max(float(act.max()) if len(act) else 0.0, 0.05)
    for i, a in enumerate(act):
        x = pad + i * (width - 2 * pad) / n
        y = height - pad - (height - 2 * pad) * min(a / peak, 1.0)
        d.line([(x, height - pad), (x, y)], fill=(40, 40, 40))
    for c in result["cuts"]:
        x = pad + c["frame"] * (width - 2 * pad) / n
        d.line([(x, pad), (x, height - pad)], fill=(220, 40, 40), width=2)
    if score:
        for b in score.get("beats", []):
            x = pad + b["start"] * fps * (width - 2 * pad) / n
            d.line([(x, pad), (x, pad + 12)], fill=(40, 90, 220), width=3)
            d.text((x + 3, pad), b["id"], fill=(40, 90, 220))
    d.text((pad, height - pad + 4), "activity per frame · red = detected cut · blue = planned beat start",
           fill=(90, 90, 90))
    img.save(path)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--score", type=Path)
    a = ap.parse_args()

    frames, fps = read_frames(a.video)
    result = analyse(frames, fps)
    a.out.mkdir(parents=True, exist_ok=True)
    with open(a.out / "strip.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["frame", "t", "activity"])
        for i, v in enumerate(result["activity"]):
            w.writerow([i, round(i / fps, 3), round(float(v), 5)])
    summary = {k: v for k, v in result.items() if k != "activity"}
    write_json(a.out / "strip.json", summary)
    draw(result, load_json(a.score) if a.score else None, a.out / "strip.png")
    print(f"{len(result['cuts'])} cuts, {len(result['still_runs'])} still runs → {a.out}")


if __name__ == "__main__":
    main()
