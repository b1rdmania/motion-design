#!/usr/bin/env python3
"""Loudness, true peak, clipping, silences and onsets for a rendered video or audio file.

    python3 audio_check.py video.mp4 --out review/audio.json [--silence-db -50] [--min-silence 0.25]

The onset list is a plain energy-rise detector. It is a hint, not a beat tracker.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _common import need, probe, run, write_json  # noqa: E402

SR = 48000
WIN = 0.02  # 20 ms analysis window


def loudness(path: Path) -> dict:
    out = run(["ffmpeg", "-nostats", "-i", str(path), "-map", "0:a:0", "-af", "ebur128=peak=true",
               "-f", "null", "-"], check=False)
    text = out.stderr
    summary = text[text.rfind("Summary:"):] if "Summary:" in text else ""
    i = re.search(r"I:\s+(-?[\d.]+|-inf)\s+LUFS", summary)
    tp = re.search(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf)\s+dBFS", summary, re.S)
    lra = re.search(r"LRA:\s+(-?[\d.]+)\s+LU", summary)

    def num(m):
        if not m:
            return None
        return None if m.group(1) == "-inf" else float(m.group(1))

    return {"integrated_lufs": num(i), "true_peak_dbtp": num(tp), "lra_lu": num(lra),
            "measurement_error": out.stderr[-500:] if out.returncode else None}


def samples(path: Path) -> np.ndarray:
    proc = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-ac", "2",
                           "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True)
    x = np.frombuffer(proc.stdout, dtype=np.float32)
    return x[: (x.size // 2) * 2].reshape(-1, 2)


def analyse(x: np.ndarray, silence_db: float, min_silence: float) -> dict:
    clipped = int((np.abs(x) >= 0.999).sum())
    # Combine channel energies, not amplitudes: opposite polarity is not silence.
    energy = np.mean(x.astype(np.float64) ** 2, axis=1)
    hop = int(SR * WIN)
    n = energy.size // hop
    frames = energy[: n * hop].reshape(n, hop)
    rms = np.sqrt(frames.mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms)

    silences, start = [], None
    for i, v in enumerate(db):
        quiet = v < silence_db
        if quiet and start is None:
            start = i
        if (not quiet or i == n - 1) and start is not None:
            end = i if not quiet else i + 1
            if (end - start) * WIN >= min_silence:
                silences.append({"start": round(start * WIN, 3), "end": round(end * WIN, 3),
                                 "dur": round((end - start) * WIN, 3)})
            start = None

    rise = np.diff(db, prepend=db[:1])
    onsets = []
    for i in range(1, n):
        if rise[i] > 12 and db[i] > silence_db + 10 and (not onsets or i * WIN - onsets[-1] > 0.08):
            onsets.append(round(i * WIN, 3))

    return {"clipped_samples": clipped, "silences": silences, "onsets": onsets,
            "duration": round(len(x) / SR, 3),
            "max_abs_sample": float(np.max(np.abs(x))) if x.size else 0.0,
            "analysis": {"silence_db": silence_db, "min_silence": min_silence, "window_seconds": WIN}}


def check(path: Path, silence_db: float = -50.0, min_silence: float = 0.25) -> dict:
    need("ffmpeg")
    info = probe(path)
    if not info["ok"]:
        return {"has_audio": False, "error": info["error"]}
    if not info["audio"]:
        return {"has_audio": False}
    result = {"has_audio": True, **loudness(path)}
    result.update(analyse(samples(path), silence_db, min_silence))
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("media", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--silence-db", type=float, default=-50.0)
    ap.add_argument("--min-silence", type=float, default=0.25)
    a = ap.parse_args()
    result = check(a.media, a.silence_db, a.min_silence)
    write_json(a.out, result)
    if result.get("has_audio"):
        print(f"{result['integrated_lufs']} LUFS, TP {result['true_peak_dbtp']} dBTP, "
              f"{result['clipped_samples']} clipped, {len(result['silences'])} silences → {a.out}")
    else:
        print(f"no audio → {a.out}")


if __name__ == "__main__":
    main()
