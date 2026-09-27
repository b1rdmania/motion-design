#!/usr/bin/env python3
"""Write a rough audiomap.json for a music track: tempo, beat grid, onsets, bass
entries and an energy curve. numpy only. It is a starting point to check by ear and
by eye, not a beat tracker you can trust blindly; on calm or rubato music, place cue
points by hand instead.

    python3 beatmap.py track.wav --out plan/audiomap.json
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _common import need, write_json  # noqa: E402

SR = 22050
HOP = 512


def load(path: Path) -> np.ndarray:
    need("ffmpeg")
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True)
    return np.frombuffer(out.stdout, dtype=np.float32).astype(np.float64)


def analyse(x: np.ndarray) -> dict:
    n = max(0, (len(x) - 2048) // HOP)
    if n < 8:
        return {"duration": round(len(x) / SR, 3), "bpm": None, "beats_sec": [], "onsets": [], "low_onsets": [],
                "energy": []}
    idx = np.arange(2048)[None, :] + HOP * np.arange(n)[:, None]
    spec = np.abs(np.fft.rfft(x[idx] * np.hanning(2048), axis=1))
    freqs = np.fft.rfftfreq(2048, 1 / SR)
    flux = np.maximum(np.diff(np.log1p(spec), axis=0), 0).sum(axis=1)
    flux = np.concatenate([[0], flux])
    flux = (flux - flux.mean()) / (flux.std() + 1e-9)
    fps = SR / HOP

    # tempo by autocorrelation of the onset envelope, 60–180 BPM
    ac = np.correlate(flux, flux, mode="full")[n - 1:]
    lags = np.arange(len(ac))
    lo, hi = int(fps * 60 / 180), int(fps * 60 / 60)
    lag = lo + int(np.argmax(ac[lo:hi])) if hi > lo and hi < len(ac) else None
    bpm = round(60 * fps / lag, 1) if lag else None

    beats = []
    if lag:
        phases = [flux[p::lag].sum() for p in range(lag)]
        p = int(np.argmax(phases))
        beats = [round(i / fps, 3) for i in range(p, n, lag)]

    peaks = [i for i in range(1, n - 1) if flux[i] > 1.5 and flux[i] >= flux[i - 1] and flux[i] > flux[i + 1]]
    onsets = [round(i / fps, 3) for i in peaks]

    low = spec[:, (freqs > 20) & (freqs < 150)].sum(axis=1)
    low_db = 20 * np.log10(low + 1e-9)
    rise = np.diff(low_db, prepend=low_db[:1])
    floor = np.percentile(low_db, 20)
    low_onsets, last = [], -1.0
    for i in range(n):
        if rise[i] > 8 and low_db[i] > floor + 15 and i / fps - last > 0.15:
            low_onsets.append(round(i / fps, 3))
            last = i / fps

    rms = np.sqrt((x[idx] ** 2).mean(axis=1))
    step = int(fps / 2)
    energy = [round(float(20 * np.log10(rms[i:i + step].mean() + 1e-9)), 1) for i in range(0, n, step)]

    return {"duration": round(len(x) / SR, 3), "bpm": bpm, "beats_sec": beats, "onsets": onsets,
            "low_onsets": low_onsets, "energy_db_per_half_second": energy,
            "note": "heuristic analysis; check the grid and key moments by ear before timing cuts to them"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("track", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    result = analyse(load(a.track))
    write_json(a.out, result)
    print(f"{result['bpm']} BPM · {len(result['beats_sec'])} beats · {len(result['onsets'])} onsets · "
          f"{len(result['low_onsets'])} bass entries → {a.out}")


if __name__ == "__main__":
    main()
