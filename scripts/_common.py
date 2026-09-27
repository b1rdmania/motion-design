"""Shared helpers for the motion-design review scripts. No model calls."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

PLAN_FILES = ("treatment.md", "score.json", "evidence.json")


def need(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        raise SystemExit(f"{tool} not found on PATH")
    return path


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def plan_version(plan_dir: Path) -> str:
    """Hash of treatment + score + evidence. score.plan_version is excluded so the
    hash is stable after it is written back."""
    h = hashlib.sha256()
    for name in PLAN_FILES:
        p = plan_dir / name
        if not p.exists():
            continue
        data = p.read_bytes()
        if name == "score.json":
            obj = json.loads(data)
            obj.pop("plan_version", None)
            data = json.dumps(obj, sort_keys=True).encode()
        h.update(name.encode() + b"\0" + data + b"\0")
    return h.hexdigest()[:16]


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def probe(video: Path) -> dict:
    need("ffprobe")
    out = run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)
    ], check=False)
    if out.returncode != 0:
        return {"ok": False, "error": out.stderr.strip()}
    data = json.loads(out.stdout)
    info = {"ok": True, "duration": float(data["format"].get("duration", 0)), "video": None, "audio": None}
    for s in data.get("streams", []):
        if s["codec_type"] == "video" and info["video"] is None:
            num, den = s.get("avg_frame_rate", "0/1").split("/")
            fps = float(num) / float(den) if float(den) else 0.0
            info["video"] = {"width": s["width"], "height": s["height"], "fps": round(fps, 3)}
        elif s["codec_type"] == "audio" and info["audio"] is None:
            info["audio"] = {"sample_rate": int(s.get("sample_rate", 0)), "channels": s.get("channels", 0)}
    return info


def beats(score: dict) -> list[dict]:
    return score.get("beats", [])


def frame_tol(score: dict, frames: int = 2) -> float:
    return frames / float(score.get("fps", 24))
