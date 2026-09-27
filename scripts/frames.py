#!/usr/bin/env python3
"""Extract review samples from a render and build labelled contact sheets.

    python3 frames.py video.mp4 --score plan/score.json --stage final --out review/r1/frames \
        [--view-width 375] [--at 12.4,18.0]

Stages:
  style_frames  one frame per beat, mid-hold
  animatic      per beat: hold start, hold end, both sides of each transition
  final         same as animatic

Writes PNGs, frames.json (manifest) and contact-*.png. With --view-width it also
writes a sheet scaled to that width, for legibility at the intended viewing size.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from _common import need, probe, run, write_json, load_json, text_cues  # noqa: E402


def sample_times(score: dict, stage: str, duration: float, extra: list[float]) -> list[dict]:
    fps = float(score.get("fps", 24))
    one = 1.0 / fps
    out = []
    if stage != "style_frames":
        out.append({"beat": (score.get("beats") or [{}])[0].get("id"), "kind": "first-frame", "t": 0.0})
    for i, b in enumerate(score.get("beats", [])):
        start, dur = float(b["start"]), float(b["dur"])
        end = start + dur
        build = float((b.get("motion") or {}).get("build", 0) or 0)
        hold_start = min(start + build, end - one)
        if stage == "style_frames":
            out.append({"beat": b["id"], "kind": "hold", "t": (hold_start + end) / 2})
            continue
        if i > 0:
            out.append({"beat": b["id"], "kind": "transition-before", "t": start - 3 * one})
            out.append({"beat": b["id"], "kind": "transition-after", "t": start + 2 * one})
        out.append({"beat": b["id"], "kind": "hold-start", "t": hold_start})
        out.append({"beat": b["id"], "kind": "hold-end", "t": end - 2 * one})
        for cue in text_cues(b):
            cue_start = start + float(cue.get("start", 0))
            cue_end = cue_start + float(cue.get("hold", 0))
            out.append({"beat": b["id"], "kind": "text-start", "t": cue_start})
            out.append({"beat": b["id"], "kind": "text-end", "t": max(cue_start, cue_end - one)})
    for t in extra:
        out.append({"beat": None, "kind": "flagged", "t": t})
    for s in out:
        s["t"] = round(min(max(s["t"], 0.0), max(duration - one, 0.0)), 3)
    return out


def extract(video: Path, t: float, path: Path) -> None:
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", str(path)])


def sheet(items: list[dict], path: Path, width: int | None, cols: int = 4) -> None:
    imgs = []
    for it in items:
        im = Image.open(it["path"]).convert("RGB")
        if width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        else:
            im.thumbnail((640, 640))
        imgs.append(im)
    if not imgs:
        return
    cw, ch, label = max(i.width for i in imgs), max(i.height for i in imgs), 22
    rows = (len(imgs) + cols - 1) // cols
    out = Image.new("RGB", (cols * cw, rows * (ch + label)), "white")
    d = ImageDraw.Draw(out)
    for k, (im, it) in enumerate(zip(imgs, items)):
        x, y = (k % cols) * cw, (k // cols) * (ch + label)
        out.paste(im, (x, y + label))
        d.text((x + 4, y + 4), f"{it['beat'] or '-'} · {it['kind']} · {it['t']:.2f}s", fill=(0, 0, 0))
    out.save(path)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video", type=Path)
    ap.add_argument("--score", type=Path, required=True)
    ap.add_argument("--stage", choices=["style_frames", "animatic", "final"], required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--view-width", type=int)
    ap.add_argument("--at", default="", help="extra comma-separated timestamps to sample")
    a = ap.parse_args()

    need("ffmpeg")
    info = probe(a.video)
    if not info["ok"]:
        raise SystemExit(info["error"])
    score = load_json(a.score)
    extra = [float(t) for t in a.at.split(",") if t.strip()]
    items = sample_times(score, a.stage, info["duration"], extra)
    a.out.mkdir(parents=True, exist_ok=True)
    for k, it in enumerate(items):
        p = a.out / f"{k:03d}-{it['beat'] or 'x'}-{it['kind']}.png"
        extract(a.video, it["t"], p)
        it["path"] = str(p)
    sheet(items, a.out / "contact.png", None)
    if a.view_width:
        sheet(items, a.out / f"contact-{a.view_width}px.png", a.view_width)
    write_json(a.out / "frames.json", {"stage": a.stage, "view_width": a.view_width, "samples": items})
    print(f"{len(items)} samples → {a.out}")


if __name__ == "__main__":
    main()
