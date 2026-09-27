#!/usr/bin/env python3
"""Review a render against its own plan. Writes critique.json with measured findings
and the judged items the agent must resolve by looking at the frames.

    python3 check.py --plan plan/ --video renders/draft.mp4 --stage animatic --round 1 \
        --out review/animatic-r1 [--view-width 375] [--audiomap plan/audiomap.json]

    python3 check.py --plan plan/ --stills renders/style/ --stage style_frames --out review/style-r1

Statuses: pass, fail, needs_review, not_applicable. An uncertain machine result is
needs_review. Only findings with blocking=true can stop delivery. Defaults are advice.
"""

from __future__ import annotations

import argparse
import re
import statistics
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import audio_check  # noqa: E402
import frames as frames_mod  # noqa: E402
import motion_strip  # noqa: E402
from _common import load_json, plan_version, probe, run, sha256_file, write_json  # noqa: E402

REF = {
    "integrity": "references/review.md#artifact-integrity",
    "communication": "references/review.md#communication",
    "evidence": "references/evidence.md",
    "sound": "references/sound.md#integrity",
    "fidelity": "references/review.md#fidelity",
    "default": "references/defaults.md",
    "judged": "references/review.md#judged",
}

STOCK = [
    r"\bintroducing\b", r"^meet\b", r"say goodbye to", r"imagine a world", r"in today'?s fast[- ]paced",
    r"what if i told you", r"the future of .+ is here", r"harness the power", r"game[- ]chang",
    r"next level", r"single source of truth", r"we'?ve got you covered", r"it'?s that simple",
    r"but that'?s not all", r"unlock\b", r"seamless(ly)?\b", r"revolutioni[sz]e",
]


class Review:
    def __init__(self, score: dict, overrides: dict):
        self.findings: list[dict] = []
        self.overridden: list[dict] = []
        self.score = score
        self.overrides = overrides

    def add(self, rule: str, status: str, blocking: bool, *, beat=None, t=None, evidence=None, fix=None):
        if rule in self.overrides and rule.startswith("default."):
            self.overridden.append({"rule": rule, "reason": self.overrides[rule], "beat": beat})
            return
        self.findings.append({
            "rule": rule, "source": REF[rule.split(".")[0]], "status": status, "blocking": blocking,
            "beat": beat, "t": None if t is None else round(float(t), 3),
            "evidence": evidence, "fix": fix,
        })


def text_of(b: dict) -> tuple[str, str]:
    sup = b.get("super") or {}
    return (sup.get("text", "") if isinstance(sup, dict) else str(sup)), (b.get("vo") or "")


def expected_events(score: dict) -> list[dict]:
    events = [dict(e) for e in score.get("events", [])]
    have = {(e["type"], round(float(e["t"]), 2)) for e in events}
    for i, b in enumerate(score.get("beats", [])):
        if i > 0 and b.get("transition_in", "cut") == "cut" and ("cut", round(float(b["start"]), 2)) not in have:
            events.append({"type": "cut", "t": float(b["start"]), "beat": b["id"], "derived": True})
    return sorted(events, key=lambda e: float(e["t"]))


def beat_at(score: dict, t: float):
    for b in score.get("beats", []):
        if b["start"] <= t < b["start"] + b["dur"]:
            return b["id"]
    return None


# ---------------------------------------------------------------- integrity

def integrity(r: Review, video: Path, info: dict, delivery: dict, fps: float):
    if not info["ok"] or not info["video"]:
        r.add("integrity.decode", "fail", True, evidence=info.get("error", "no video stream"),
              fix="re-render; the file does not decode")
        return False
    errs = run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"], check=False).stderr.strip()
    r.add("integrity.decode", "fail" if errs else "pass", True, evidence=errs[:500] or "full decode clean",
          fix="re-render; decoder reported errors" if errs else None)

    v = info["video"]
    formats = delivery.get("formats", [])
    if formats:
        match = [f for f in formats if f["width"] == v["width"] and f["height"] == v["height"]]
        r.add("integrity.dimensions", "pass" if match else "fail", True,
              evidence=f"{v['width']}x{v['height']}; delivery allows "
                       + ", ".join(f"{f['width']}x{f['height']}" for f in formats),
              fix=None if match else "render at a delivery size")
    else:
        r.add("integrity.dimensions", "needs_review", True, evidence="score.delivery.formats is empty",
              fix="declare the delivery sizes in score.json")

    r.add("integrity.fps", "pass" if abs(v["fps"] - fps) < 0.01 else "fail", True,
          evidence=f"render {v['fps']} fps; score {fps} fps")

    want = float(r.score.get("duration", 0))
    tol = 2.0 / fps
    ok = abs(info["duration"] - want) <= tol
    r.add("integrity.duration", "pass" if ok else "fail", True,
          evidence=f"render {info['duration']:.3f}s; score {want:.3f}s; tolerance ±2 frames")

    expects_audio = delivery.get("audio")
    if expects_audio is None:
        expects_audio = bool(r.score.get("music")) or any(b.get("vo") or (b.get("sound") or {}).get("cues")
                                                          for b in r.score.get("beats", []))
    if expects_audio:
        r.add("integrity.audio_present", "pass" if info["audio"] else "fail", True,
              evidence="audio stream present" if info["audio"] else "no audio stream; score plans sound")
    return True


def flat_frames(r: Review, samples: list[dict]):
    seen = set()
    for s in samples:
        if s["beat"] in seen:
            continue
        im = np.asarray(Image.open(s["path"]).convert("L"), dtype=np.float32)
        if im.std() < 1.5:
            seen.add(s["beat"])
            r.add("integrity.flat_frame", "needs_review", False, beat=s["beat"], t=s["t"],
                  evidence=f"{s['path']} is a flat field (std {im.std():.2f}); missing media or an intended plate",
                  fix="confirm the frame is intended; if not, the asset failed to load")


# ------------------------------------------------------------ communication

def communication(r: Review, stage: str, sheet: str | None):
    beats = r.score.get("beats", [])
    supers = [(b, *text_of(b)) for b in beats]
    if not any(s or v for _, s, v in supers):
        r.add("communication.text", "not_applicable", True, evidence="no supers or VO in the score")
        return
    for b, sup, vo in supers:
        if not sup:
            continue
        chars = len(sup.replace("\n", " ").strip())
        sd = b.get("super") if isinstance(b.get("super"), dict) else {}
        build = float((b.get("motion") or {}).get("build", 0) or 0)
        hold = float(sd.get("hold") or (b["dur"] - build))
        cps = chars / hold if hold > 0 else float("inf")
        r.add("communication.reading_time", "fail" if cps > 25 else "pass", True, beat=b["id"], t=b["start"],
              evidence=f"{chars} chars held {hold:.2f}s = {cps:.1f} cps (hard limit 25)",
              fix=f"hold at least {chars / 25:.2f}s or cut words" if cps > 25 else None)
        if stage != "animatic":
            r.add("communication.legible_at_view", "needs_review", True, beat=b["id"], t=b["start"],
                  evidence=f"read '{sup}' on {sheet or 'the contact sheet'}",
                  fix="judge size, contrast and hierarchy at the intended viewing width")
    if any(v for _, _, v in supers) and stage != "style_frames":
        r.add("communication.speech", "needs_review", True,
              evidence="speech intelligibility is not measured by script",
              fix="check VO level against the music bed (ducking) and the TTS render for slurred words")


# ------------------------------------------------------------------ evidence

def evidence(r: Review, ledger: dict):
    claims = {c["id"]: c for c in ledger.get("claims", [])}
    beats = r.score.get("beats", [])
    touched = False
    for c in claims.values():
        if c.get("type") == "fact" and not (c.get("source") and c.get("evidence")):
            touched = True
            r.add("evidence.fact_supported", "fail", True, evidence=f"claim {c['id']} has no source or evidence",
                  fix="add the source and the supporting excerpt, or downgrade it to inference")
    for b in beats:
        sup, vo = text_of(b)
        words = f"{sup} {vo}".strip()
        pid = b.get("proves")
        ids = pid if isinstance(pid, list) else ([pid] if pid else [])
        for i in ids:
            touched = True
            if i not in claims:
                r.add("evidence.claim_exists", "fail", True, beat=b["id"], t=b["start"],
                      evidence=f"beat proves '{i}', which is not in evidence.json", fix="add the claim or remove it")
                continue
            c = claims[i]
            if c.get("type") == "metaphor":
                r.add("evidence.metaphor_wording", "needs_review", True, beat=b["id"], t=b["start"],
                      evidence=f"metaphor {i}; limits: {c.get('limits', '—')}",
                      fix="confirm the image and words do not present the metaphor as a fact")
            pw = c.get("permitted_wording")
            if pw and words and pw.lower() not in words.lower() and words.lower() not in pw.lower():
                r.add("evidence.permitted_wording", "needs_review", True, beat=b["id"], t=b["start"],
                      evidence=f"on screen: '{words}'; permitted: '{pw}'",
                      fix="use the permitted wording or record why the new wording is still supported")
        if re.search(r"\d", words) and not ids:
            touched = True
            r.add("evidence.number_anchored", "fail", True, beat=b["id"], t=b["start"],
                  evidence=f"'{words}' contains a number and no evidence id",
                  fix="add a claim to evidence.json and set beat.proves")
    if not touched:
        r.add("evidence.claims", "not_applicable", True, evidence="no claims or numbers in the film")


# --------------------------------------------------------------------- sound

def sound(r: Review, audio: dict, delivery: dict, events: list[dict], stage: str):
    if not audio.get("has_audio"):
        return
    r.add("sound.clipping", "fail" if audio["clipped_samples"] else "pass", True,
          evidence=f"{audio['clipped_samples']} samples at full scale",
          fix="lower the master or add a true-peak limiter" if audio["clipped_samples"] else None)
    target = float(delivery.get("loudness_lufs", -14))
    tol = float(delivery.get("loudness_tolerance", 1))
    tp_max = float(delivery.get("true_peak_dbtp", -1))
    lufs, tp = audio.get("integrated_lufs"), audio.get("true_peak_dbtp")
    if stage == "final":
        if lufs is None:
            r.add("sound.loudness", "not_applicable", True, evidence="no gated programme loudness (intended silence)")
        else:
            ok = abs(lufs - target) <= tol
            r.add("sound.loudness", "pass" if ok else "fail", True,
                  evidence=f"{lufs} LUFS integrated; target {target} ±{tol}",
                  fix=None if ok else f"loudnorm to I={target}:TP={tp_max}")
        if tp is not None:
            r.add("sound.true_peak", "pass" if tp <= tp_max else "fail", True,
                  evidence=f"{tp} dBTP; maximum {tp_max}")
    tol_s = 2.0 / float(r.score.get("fps", 24)) + 0.04
    declared = [e for e in events if e["type"] == "silence"]
    for s in audio.get("silences", []):
        planned = any(abs(s["start"] - float(e["t"])) <= tol_s + 0.1 for e in declared)
        at_edge = s["start"] <= 0.05 or s["end"] >= audio["duration"] - 0.05
        if not planned and not at_edge:
            r.add("sound.unplanned_gap", "needs_review", True, t=s["start"], beat=beat_at(r.score, s["start"]),
                  evidence=f"silence {s['start']}–{s['end']}s is not in score.events",
                  fix="declare it as a silence event, or fix the gap in the audio assembly")
    if stage != "style_frames":
        r.add("sound.repeats", "needs_review", True,
              evidence="repeated or doubled audio is not measured by script",
              fix="read the audio timeline or assembly log for clips placed twice or overlapping tails")


# ------------------------------------------------------------------ fidelity

def fidelity(r: Review, strip: dict, audio: dict, events: list[dict], stage: str):
    fps = float(r.score.get("fps", 24))
    tol = 2.0 / fps
    cuts = [c["t"] for c in strip.get("cuts", [])]
    for e in events:
        t, kind = float(e["t"]), e["type"]
        beat = e.get("beat") or beat_at(r.score, t)
        if kind == "cut":
            near = min((abs(c - t) for c in cuts), default=None)
            ok = near is not None and near <= tol + 1e-6
            r.add("fidelity.cut", "pass" if ok else "fail", True, beat=beat, t=t,
                  evidence=f"nearest detected cut {near:.3f}s away" if near is not None else "no cuts detected",
                  fix=None if ok else "the cut is missing or off by more than 2 frames")
        elif kind == "silence" and audio.get("has_audio"):
            near = min((abs(s["start"] - t) for s in audio.get("silences", [])), default=None)
            ok = near is not None and near <= tol + 0.04
            r.add("fidelity.silence", "pass" if ok else "fail", True, beat=beat, t=t,
                  evidence=f"nearest detected silence starts {near:.3f}s away" if near is not None
                  else "no silence detected", fix=None if ok else "the planned silence is missing or late")
        elif kind == "hit" and audio.get("has_audio"):
            near = min((abs(o - t) for o in audio.get("onsets", [])), default=None)
            ok = near is not None and near <= tol + 0.02
            r.add("fidelity.hit", "pass" if ok else "needs_review", True, beat=beat, t=t,
                  evidence=f"nearest onset {near:.3f}s away" if near is not None else "no onset detected",
                  fix=None if ok else "confirm the hit lands; the onset detector is a hint")
    planned = [float(e["t"]) for e in events if e["type"] == "cut"]
    for c in cuts:
        if not any(abs(c - p) <= tol for p in planned):
            r.add("fidelity.unplanned_cut", "needs_review", False, t=c, beat=beat_at(r.score, c),
                  evidence=f"cut detected at {c}s with no planned cut", fix="a flash, a pop or an unplanned edit?")
    for b in r.score.get("beats", []):
        hold = float((b.get("motion") or {}).get("hold", 0) or 0)
        if hold <= 0 or stage == "style_frames":
            continue
        s, e = b["start"], b["start"] + b["dur"]
        best = max((min(run_["end"], e) - max(run_["start"], s) for run_ in strip.get("still_runs", [])), default=0)
        r.add("fidelity.hold", "pass" if best >= 0.8 * hold else "needs_review", False, beat=b["id"], t=s,
              evidence=f"longest still run in beat {max(best, 0):.2f}s; planned hold {hold:.2f}s",
              fix=None if best >= 0.8 * hold else "holds with drift or grain read as motion; check the frames")


def commitments(r: Review, stage: str):
    if stage not in ("style_frames", "final"):
        return
    for b in r.score.get("beats", []):
        for c in b.get("commitments", []):
            r.add("fidelity.commitment", "needs_review", True, beat=b["id"], t=b["start"],
                  evidence=f"mandatory: {c}", fix="confirm it is present and exact in the frame")


# ------------------------------------------------------------------ defaults

def defaults(r: Review, audiomap: dict | None, events: list[dict]):
    beats = r.score.get("beats", [])
    fps = float(r.score.get("fps", 24))
    for b in beats:
        m = b.get("motion") or {}
        build, hold = float(m.get("build", 0) or 0), float(m.get("hold", 0) or 0)
        if build and hold and hold < build:
            r.add("default.hold_ge_build", "fail", False, beat=b["id"], t=b["start"],
                  evidence=f"build {build}s, hold {hold}s", fix="hold at least as long as the build, or override")
        if b["dur"] < 1 and build > 0:
            r.add("default.no_short_animation", "fail", False, beat=b["id"], t=b["start"],
                  evidence=f"{b['dur']}s beat animates for {build}s", fix="hard cut to the resolved state")
        sup, vo = text_of(b)
        if sup:
            sd = b.get("super") if isinstance(b.get("super"), dict) else {}
            h = float(sd.get("hold") or (b["dur"] - build))
            chars = len(sup.replace("\n", " ").strip())
            if h > 0 and chars / h > 17:
                r.add("default.super_speed", "fail", False, beat=b["id"], t=b["start"],
                      evidence=f"{chars / h:.1f} cps (default ≤ 17)")
            lines = sup.split("\n")
            if len(lines) > 2 or max(len(x) for x in lines) > 42:
                r.add("default.super_shape", "fail", False, beat=b["id"], t=b["start"],
                      evidence=f"{len(lines)} lines, longest {max(len(x) for x in lines)} chars (default ≤ 2, ≤ 42)")
        for pat in STOCK:
            for field in (sup, vo):
                if field and re.search(pat, field, re.I):
                    r.add("default.stock_copy", "fail", False, beat=b["id"], t=b["start"],
                          evidence=f"'{field}' matches /{pat}/", fix="say the specific thing instead")
    if len(beats) >= 3:
        durs = [float(b["dur"]) for b in beats]
        cv = statistics.pstdev(durs) / statistics.mean(durs)
        if cv < 0.25:
            r.add("default.pace_varies", "fail", False, evidence=f"beat-length variation {cv:.2f} (default ≥ 0.25)",
                  fix="vary beat lengths with their weight, or override for a deliberately even film")
    words = sum(len(text_of(b)[1].split()) for b in beats)
    dur = float(r.score.get("duration", 0)) or 1
    if words / dur > 2.5:
        r.add("default.vo_budget", "fail", False, evidence=f"{words} VO words in {dur:.1f}s = {words / dur:.2f}/s (default ≤ 2.5)")
    for e in events:
        if e["type"] == "silence" and float(e["t"]) < 0.5:
            r.add("default.no_silence_at_top", "fail", False, t=e["t"], evidence="planned silence at the top")
    grid = []
    if audiomap:
        grid = audiomap.get("beats_sec") or [p.get("start") for p in audiomap.get("phrases", []) if "start" in p]
    if r.score.get("lead") == "music" and grid:
        tol = 2.0 / fps
        for e in events:
            if e["type"] == "cut" and not any(abs(float(e["t"]) - g) <= tol for g in grid):
                r.add("default.cut_on_phrase", "fail", False, t=e["t"], beat=e.get("beat"),
                      evidence="cut is more than 2 frames from any beat or phrase in the audiomap")


# -------------------------------------------------------------------- judged

def judged(r: Review, stage: str, sheet: str | None, strip_png: str | None):
    beats = r.score.get("beats", [])
    if stage in ("style_frames", "final"):
        for b in beats:
            r.add("judged.frame", "needs_review", False, beat=b["id"], t=b["start"],
                  evidence=f"job: {b.get('job', '—')} · focal: {b.get('focal', '—')} · see {sheet}",
                  fix="Does the frame carry its job? One focal point? On brand? Does it follow a reference?")
        r.add("judged.reskin", "needs_review", False, evidence=f"see {sheet}",
              fix="Could these frames serve another brand with a text swap? If yes, the concept is not native.")
    if stage in ("animatic", "final"):
        for i, b in enumerate(beats):
            tr = b.get("transition_in", "cut")
            if i > 0 and tr != "cut":
                r.add("judged.transition", "needs_review", False, beat=b["id"], t=b["start"],
                      evidence=f"declared {tr}; see transition samples",
                      fix="Does the shared property survive the boundary? A near miss reads worse than a cut.")
        r.add("judged.pacing", "needs_review", False, evidence=f"see {strip_png} against the feeling progression",
              fix="Does the rhythm follow the treatment? Activity is measured; good pacing is judged.")


# ---------------------------------------------------------------------- main

def verdict(findings: list[dict]) -> str:
    if any(f["blocking"] and f["status"] == "fail" for f in findings):
        return "blocked"
    if any(f["blocking"] and f["status"] == "needs_review" for f in findings):
        return "open"
    return "clear"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--video", type=Path)
    ap.add_argument("--stills", type=Path, help="style-frame PNGs named <beat-id>.png")
    ap.add_argument("--stage", choices=["style_frames", "animatic", "final"], required=True)
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--view-width", type=int)
    ap.add_argument("--audiomap", type=Path)
    a = ap.parse_args()

    score = load_json(a.plan / "score.json")
    if score is None:
        raise SystemExit(f"{a.plan}/score.json not found; write the plan before reviewing")
    ledger = load_json(a.plan / "evidence.json", {"claims": []})
    overrides = {o["rule"]: o["reason"] for o in score.get("overrides", [])}
    delivery = score.get("delivery", {})
    fps = float(score.get("fps", 24))
    view_width = a.view_width or delivery.get("view_width")
    events = expected_events(score)
    r = Review(score, overrides)
    a.out.mkdir(parents=True, exist_ok=True)
    strip, audio, sheet, strip_png, render_hash = {}, {"has_audio": False}, None, None, None

    if a.stills:
        render_hash = "stills"
        samples = []
        for b in score.get("beats", []):
            p = a.stills / f"{b['id']}.png"
            if not p.exists():
                r.add("integrity.style_frame_missing", "fail", True, beat=b["id"], evidence=f"{p} not found")
                continue
            samples.append({"beat": b["id"], "kind": "style", "t": b["start"], "path": str(p)})
        frames_mod.sheet(samples, a.out / "contact.png", None)
        sheet = str(a.out / "contact.png")
        if view_width:
            frames_mod.sheet(samples, a.out / f"contact-{view_width}px.png", view_width)
            sheet = str(a.out / f"contact-{view_width}px.png")
        flat_frames(r, samples)
    else:
        if not a.video:
            raise SystemExit("--video or --stills is required")
        info = probe(a.video)
        render_hash = sha256_file(a.video) if a.video.exists() else None
        if integrity(r, a.video, info, delivery, fps):
            raw, vfps = motion_strip.read_frames(a.video)
            res = motion_strip.analyse(raw, vfps)
            strip = {k: v for k, v in res.items() if k != "activity"}
            write_json(a.out / "strip.json", strip)
            motion_strip.draw(res, score, a.out / "strip.png")
            strip_png = str(a.out / "strip.png")
            audio = audio_check.check(a.video)
            write_json(a.out / "audio.json", audio)
            samples = frames_mod.sample_times(score, a.stage, info["duration"], [])
            fdir = a.out / "frames"
            fdir.mkdir(exist_ok=True)
            for k, s in enumerate(samples):
                p = fdir / f"{k:03d}-{s['beat'] or 'x'}-{s['kind']}.png"
                frames_mod.extract(a.video, s["t"], p)
                s["path"] = str(p)
            write_json(fdir / "frames.json", {"stage": a.stage, "samples": samples})
            frames_mod.sheet(samples, a.out / "contact.png", None)
            sheet = str(a.out / "contact.png")
            if view_width:
                frames_mod.sheet(samples, a.out / f"contact-{view_width}px.png", view_width)
                sheet = str(a.out / f"contact-{view_width}px.png")
            flat_frames(r, samples)
            sound(r, audio, delivery, events, a.stage)
            fidelity(r, strip, audio, events, a.stage)

    communication(r, a.stage, sheet)
    evidence(r, ledger)
    commitments(r, a.stage)
    defaults(r, load_json(a.audiomap) if a.audiomap else None, events)
    judged(r, a.stage, sheet, strip_png)

    order = {"fail": 0, "needs_review": 1, "pass": 2, "not_applicable": 3}
    r.findings.sort(key=lambda f: (not f["blocking"], order[f["status"]], f["t"] if f["t"] is not None else -1))
    critique = {
        "stage": a.stage,
        "round": a.round,
        "render": str(a.video or a.stills),
        "render_sha256": render_hash,
        "plan_version": plan_version(a.plan),
        "verdict": verdict(r.findings),
        "counts": {s: sum(f["status"] == s for f in r.findings) for s in order},
        "blocking_open": sum(f["blocking"] and f["status"] in ("fail", "needs_review") for f in r.findings),
        "calibration": "defaults are not calibrated",
        "contact_sheet": sheet,
        "strip": strip_png,
        "findings": r.findings,
        "overridden": r.overridden,
        "unresolved": [],
    }
    write_json(a.out / "critique.json", critique)
    c = critique["counts"]
    print(f"{critique['verdict']}: {critique['blocking_open']} blocking open · "
          f"{c['fail']} fail · {c['needs_review']} needs_review · {c['pass']} pass → {a.out / 'critique.json'}")


if __name__ == "__main__":
    main()
