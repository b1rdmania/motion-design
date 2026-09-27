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
from _common import load_json, plan_version, probe, run, sha256_file, write_json, transition, text_cues, review_summary  # noqa: E402

REF = {
    "integrity": "references/review.md#artifact-integrity",
    "communication": "references/review.md#communication",
    "evidence": "references/evidence.md",
    "sound": "references/sound.md#integrity",
    "fidelity": "references/review.md#fidelity",
    "default": "references/defaults.md",
    "judged": "references/review.md#judged",
    "plan": "references/score.md",
}

DIGITS = re.compile(r"\d|%|\bper ?cent\b", re.I)
NUMBER_WORDS = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|"
    r"sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
    r"hundred|thousand|million|billion|half|twice|double|triple|dozen|\w+fold)\b"
    r"|\btimes (faster|more|less|cheaper|quicker|bigger|smaller)\b", re.I)

STOCK = [
    r"\bintroducing\b", r"^meet\b", r"say goodbye to", r"imagine a world", r"in today'?s fast[- ]paced",
    r"what if i told you", r"the future of .+ is here", r"harness the power", r"game[- ]chang",
    r"next level", r"single source of truth", r"we'?ve got you covered", r"it'?s that simple",
    r"but that'?s not all", r"unlock\b", r"seamless(ly)?\b", r"revolutioni[sz]e",
]


class Review:
    def __init__(self, score: dict, overrides: dict):
        self.findings: list[dict] = []
        self.overridden: list[dict] = [{"rule": k, "reason": v} for k, v in overrides.items()]
        self.score = score
        self.overrides = overrides

    def add(self, rule: str, status: str, blocking: bool, *, beat=None, t=None, evidence=None, fix=None, method="measurement"):
        if rule in self.overrides and rule.startswith("default."):
            return
        self.findings.append({
            "id": f"f{len(self.findings) + 1:04d}", "method": method,
            "rule": rule, "source": REF[rule.split(".")[0]], "status": status, "blocking": blocking,
            "beat": beat, "t": None if t is None else round(float(t), 3),
            "evidence": evidence, "fix": fix,
        })


def text_of(b: dict) -> tuple[str, str]:
    return " ".join(c.get("text", "") for c in text_cues(b)), (b.get("vo") or "")


def expected_events(score: dict) -> list[dict]:
    events = [dict(e) for e in score.get("events", [])]
    have = {(e["type"], round(float(e["t"]), 2)) for e in events}
    for i, b in enumerate(score.get("beats", [])):
        if i > 0 and transition(b).get("type") == "cut" and ("cut", round(float(b["start"]), 2)) not in have:
            events.append({"type": "cut", "t": float(b["start"]), "beat": b["id"], "derived": True})
    return sorted(events, key=lambda e: float(e["t"]))


def beat_at(score: dict, t: float):
    for b in score.get("beats", []):
        if b["start"] <= t < b["start"] + b["dur"]:
            return b["id"]
    return None


# ---------------------------------------------------------------- integrity

def integrity(r: Review, video: Path, info: dict, delivery: dict, fps: float, stage: str = "final"):
    if not info["ok"] or not info["video"]:
        r.add("integrity.decode", "fail", True, evidence=info.get("error", "no video stream"),
              fix="re-render; the file does not decode")
        return False
    decoded = run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"], check=False)
    errs = decoded.stderr.strip() or (f"decoder exit {decoded.returncode}" if decoded.returncode else "")
    r.add("integrity.decode", "fail" if errs else "pass", True, evidence=errs[:500] or "full decode clean",
          fix="re-render; decoder reported errors" if errs else None)

    v = info["video"]
    formats = delivery.get("formats", [])
    if formats:
        match = [f for f in formats if f["width"] == v["width"] and f["height"] == v["height"]]
        if not match and stage != "final":  # drafts may render smaller at the same aspect ratio
            match = [f for f in formats
                     if abs(f["width"] / f["height"] - v["width"] / v["height"]) < 0.01]
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
        for cue in text_cues(b):
            text = cue.get("text", "")
            if not text:
                continue
            chars = len(text.replace("\n", " ").strip())
            hold = float(cue.get("hold", 0))
            cps = chars / hold if hold > 0 else float("inf")
            limit = r.score.get("delivery", {}).get("max_text_cps")
            threshold = float(limit) if limit is not None else 25.0
            status = "fail" if cps > threshold else "pass"
            t = b["start"] + float(cue.get("start", 0))
            r.add("communication.reading_time_plan", status, True, beat=b["id"], t=t, method="plan",
                  evidence=f"Planned reading speed: {chars} chars / {hold:.2f}s = {cps:.1f} cps; gate {threshold:g} cps"
                           + ("" if limit is not None else " (default)")
                           + ". Checks the plan's timing, not the rendered text.",
                  fix=None if status == "pass" else
                  f"hold at least {chars / threshold:.2f}s, cut words, or set delivery.max_text_cps with a reason")
            if stage != "animatic":
                r.add("communication.legible_at_view", "needs_review", True, beat=b["id"], t=t,
                      method="inspection", evidence=f"expected '{text}'; see {sheet}",
                      fix="inspect individual frames at intended viewing width, not a scaled-down sheet")
            if stage != "style_frames":
                r.add("communication.rendered_text", "needs_review", True, beat=b["id"], t=t,
                      method="inspection", evidence=f"expected '{text}' readable for {hold:.2f}s from {t:.3f}s",
                      fix="verify actual text, appearance/disappearance times and readable hold in the video")

    if any(v for _, _, v in supers) and stage != "style_frames":
        r.add("communication.speech", "needs_review", True,
              evidence="speech intelligibility is not measured by script",
              method="inspection", fix="listen to the exported speech; if listening is unavailable, leave unresolved")


# ------------------------------------------------------------------ evidence

def evidence(r: Review, ledger: dict):
    claims = {c["id"]: c for c in ledger.get("claims", [])}
    beats = r.score.get("beats", [])
    for c in claims.values():
        if c.get("type") == "fact" and not (c.get("source") and c.get("evidence")):
            r.add("evidence.fact_supported", "fail", True, evidence=f"claim {c['id']} has no source or evidence",
                  method="plan", fix="support the claim or change/remove it; relabelling alone does not supply evidence")
    for c in claims.values():
        if c.get("type") in ("fact", "inference"):
            r.add("evidence.source_support", "needs_review", True, method="inspection",
                  evidence=f"claim {c['id']}: {c.get('source', 'no source')} / {c.get('evidence', 'no evidence')}",
                  fix="check that the actual source supports the wording and scope, not just that fields exist")
    for b in beats:
        sup, vo = text_of(b)
        r.add("evidence.coverage", "needs_review", True, beat=b["id"], t=b["start"], method="inspection",
              evidence=f"planned text/VO: {sup} {vo}; visual job: {b.get('job', '')}",
              fix="compare rendered words, speech and implied claims with the ledger; record when no claims apply")
        words = f"{sup} {vo}".strip()
        pid = b.get("proves")
        ids = pid if isinstance(pid, list) else ([pid] if pid else [])
        for i in ids:
            if i not in claims:
                r.add("evidence.claim_exists", "fail", True, beat=b["id"], t=b["start"],
                      evidence=f"beat proves '{i}', which is not in evidence.json", fix="add the claim or remove it")
                continue
            c = claims[i]
            if c.get("type") == "metaphor":
                r.add("evidence.metaphor_wording", "needs_review", True, beat=b["id"], t=b["start"],
                      evidence=f"metaphor {i}; limits: {c.get('limits', '—')}",
                      fix="confirm the image and words do not present the metaphor as a fact")
            elif c.get("type") == "sample":
                r.add("evidence.sample_labelled", "needs_review", True, beat=b["id"], t=b["start"],
                      evidence=f"sample/illustrative {i}; limits: {c.get('limits', '—')}",
                      fix="confirm the film does not present sample data or mock UI as a real result")
            pw = c.get("permitted_wording")
            if pw and words and pw.lower() not in words.lower() and words.lower() not in pw.lower():
                r.add("evidence.permitted_wording", "needs_review", True, beat=b["id"], t=b["start"],
                      evidence=f"on screen: '{words}'; permitted: '{pw}'",
                      fix="use the permitted wording or record why the new wording is still supported")
        if ids:
            continue
        if DIGITS.search(words):
            r.add("evidence.number_anchored", "needs_review", True, beat=b["id"], t=b["start"],
                  evidence=f"'{words}' contains a number and no evidence id",
                  method="heuristic", fix="distinguish quantity claims from labels/version numbers; source claims only")
        elif NUMBER_WORDS.search(words):
            r.add("evidence.number_anchored", "needs_review", True, beat=b["id"], t=b["start"],
                  evidence=f"'{words}' may state a quantity ('{NUMBER_WORDS.search(words).group(0)}') "
                           "and has no evidence id",
                  fix="if it is a quantity claim, add it to evidence.json; if not, mark pass")
    if not beats and not claims:
        r.add("evidence.claims", "needs_review", True, method="inspection",
              evidence="empty plan/ledger does not establish that the render makes no claims")


# --------------------------------------------------------------------- sound

def sound(r: Review, audio: dict, delivery: dict, events: list[dict], stage: str):
    if not audio.get("has_audio"):
        return
    r.add("sound.clipping", "needs_review" if audio["clipped_samples"] else "pass", True,
          evidence=f"{audio['clipped_samples']} samples near full scale (not proof of clipping)",
          method="heuristic", fix="inspect waveform/peak measurements for clipping" if audio["clipped_samples"] else None)
    target = float(delivery.get("loudness_lufs", -14))
    tol = float(delivery.get("loudness_tolerance", 1))
    tp_max = float(delivery.get("true_peak_dbtp", -1))
    lufs, tp = audio.get("integrated_lufs"), audio.get("true_peak_dbtp")
    if stage == "final":
        intentional_silence = delivery.get("audio") is False
        if audio.get("measurement_error"):
            r.add("sound.measurement", "needs_review", True, evidence=audio["measurement_error"],
                  fix="repair or repeat measurement; do not infer silence from an analysis failure")
        if lufs is None:
            status = "not_applicable" if intentional_silence else (
                "fail" if audio.get("max_abs_sample") == 0 and not audio.get("measurement_error") else "needs_review")
            r.add("sound.loudness", status, True,
                  evidence="silence explicitly planned" if intentional_silence else "no programme loudness despite planned/unspecified sound",
                  fix=None if intentional_silence else "check the exported audio and measurement before delivery")
        else:
            explicit = "loudness_lufs" in delivery
            ok = abs(lufs - target) <= tol
            r.add("sound.loudness", "pass" if ok else ("fail" if explicit else "needs_review"), explicit,
                  evidence=f"{lufs} LUFS; {'required' if explicit else 'suggested'} target {target} ±{tol}")
        if tp is not None:
            explicit = "true_peak_dbtp" in delivery
            r.add("sound.true_peak", "pass" if tp <= tp_max else ("fail" if explicit else "needs_review"), explicit,
                  evidence=f"{tp} dBTP; {'required' if explicit else 'suggested'} maximum {tp_max}")
        elif not intentional_silence:
            r.add("sound.true_peak", "needs_review", True, evidence="true-peak measurement unavailable")
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
              method="inspection", fix="listen to the export for unintended repeats; timeline/log inspection is supplementary, not a listening substitute")


# ------------------------------------------------------------------ fidelity

def fidelity(r: Review, strip: dict, audio: dict, events: list[dict], stage: str):
    fps = float(r.score.get("fps", 24))
    tol = 2.0 / fps
    cuts = [c["t"] for c in strip.get("cuts", [])]
    for e in events:
        t, kind = float(e["t"]), e["type"]
        tol = float(e.get("tolerance_frames", 2)) / fps
        beat = e.get("beat") or beat_at(r.score, t)
        if kind == "cut":
            near = min((abs(c - t) for c in cuts), default=None)
            ok = near is not None and near <= tol + 1e-6
            r.add("fidelity.cut", "pass" if ok else "needs_review", True, beat=beat, t=t,
                  evidence=f"nearest detected cut {near:.3f}s away" if near is not None else "no cuts detected",
                  method="heuristic", fix=None if ok else "inspect the edit: detector may miss a cut; compare renderer timing and actual frames")
        elif kind == "silence" and audio.get("has_audio"):
            candidates = audio.get("silences", [])
            found = min(candidates, key=lambda s: abs(s["start"] - t), default=None)
            end = t + float(e.get("dur", 0))
            allowance = tol + float(audio.get("analysis", {}).get("window_seconds", 0.02)) * 2
            ok = (found is not None and float(e.get("dur", 0)) > 0
                  and abs(found["start"] - t) <= allowance
                  and abs(found["end"] - end) <= allowance)
            r.add("fidelity.silence", "pass" if ok else "needs_review", True, beat=beat, t=t,
                  method="heuristic", evidence=f"planned {t:.3f}–{end:.3f}s; nearest detected {found}; tolerance {allowance:.3f}s",
                  fix=None if ok else "check both boundaries, threshold and whether this is a dropout with ambience rather than silence")
        elif kind == "hit" and audio.get("has_audio"):
            onsets = list(audio.get("onsets", [])) + list(audio.get("low_onsets", []))
            near = min((abs(o - t) for o in onsets), default=None)
            ok = near is not None and near <= tol + 0.02
            r.add("fidelity.hit", "pass" if ok else "needs_review", False, beat=beat, t=t, method="heuristic",
                  evidence=(f"nearest onset (broadband or below 150 Hz) {near:.3f}s away" if near is not None
                            else "no onset detected"),
                  fix=None if ok else "confirm the hit lands; onset detection is a hint, not a measurement")
    planned = [float(e["t"]) for e in events if e["type"] == "cut"]
    footage_spans = [(b["start"], b["start"] + b["dur"]) for b in r.score.get("beats", []) if b.get("footage")]
    for c in cuts:
        if any(s <= c < e for s, e in footage_spans):
            continue  # cuts inside embedded footage belong to that footage; fidelity.footage covers it
        if not any(abs(c - p) <= tol for p in planned):
            r.add("fidelity.unplanned_cut", "needs_review", False, t=c, beat=beat_at(r.score, c),
                  evidence=f"cut detected at {c}s with no planned cut", fix="a flash, a pop or an unplanned edit?")
    for b in r.score.get("beats", []):
        hold = float((b.get("motion") or {}).get("hold", 0) or 0)
        if hold <= 0 or stage == "style_frames" or b.get("footage"):
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
                  method="inspection", evidence=f"mandatory: {c}", fix="confirm it is present and exact in the frame")


def frame_alignment(r: Review):
    fps = float(r.score.get("fps", 24))
    off = []
    for b in r.score.get("beats", []):
        frames = float(b["start"]) * fps
        if abs(frames - round(frames)) > 0.01:
            off.append(f"{b['id']} starts at frame {frames:.2f}; use {round(frames) / fps:.4f}s")
    r.add("plan.frame_aligned", "needs_review" if off else "pass", False, method="plan",
          evidence="; ".join(off) if off else "every beat starts on a whole frame",
          fix="renderers round differently; put beat starts on whole frames" if off else None)


def footage(r: Review, video: Path, plan_dir: Path, info: dict):
    """Embedded footage must be the source, in sync and uncropped unless the plan says otherwise."""
    for b in r.score.get("beats", []):
        f = b.get("footage")
        if not f:
            continue
        src = (plan_dir / ".." / f["src"]).resolve() if not Path(f["src"]).is_absolute() else Path(f["src"])
        if not src.exists():
            r.add("fidelity.footage", "fail", True, beat=b["id"], t=b["start"], evidence=f"source {f['src']} not found")
            continue
        v = info["video"]
        x, y, w, h = f.get("rect", [0, 0, v["width"], v["height"]])
        diffs = []
        for k in (0.25, 0.5, 0.75):
            t = b["start"] + k * b["dur"]
            st = float(f.get("in", 0)) + k * b["dur"]
            a = _grab(video, t, f"crop={w}:{h}:{x}:{y},scale=160:90")
            c = _grab(src, st, "scale=160:90")
            if a is not None and c is not None:
                diffs.append(float(np.abs(a - c).mean()))
        if not diffs:
            r.add("fidelity.footage", "needs_review", True, beat=b["id"], t=b["start"], method="heuristic",
                  evidence="could not sample the footage", fix="compare the embedded clip with its source by eye")
            continue
        worst = max(diffs)
        ok = worst < 0.04
        r.add("fidelity.footage", "pass" if ok else "needs_review", True, beat=b["id"], t=b["start"],
              method="heuristic",
              evidence=f"mean abs difference vs source {', '.join(f'{d:.3f}' for d in diffs)} (pass < 0.040)",
              fix=None if ok else "check sync (in point), crop (rect) and colour against the source")


def _grab(path: Path, t: float, vf: str):
    import subprocess
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", str(path), "-frames:v", "1",
                          "-vf", vf + ",format=rgb24", "-f", "rawvideo", "-"], capture_output=True)
    if out.returncode or len(out.stdout) != 160 * 90 * 3:
        return None
    return np.frombuffer(out.stdout, dtype=np.uint8).astype(np.float32) / 255.0


# ------------------------------------------------------------------ defaults

def defaults(r: Review, audiomap: dict | None, events: list[dict]):
    """Uncalibrated prompts, not rules. Rhythm metrics are opt-in."""
    beats = r.score.get("beats", [])
    hints = set(r.score.get("review_hints", []))
    before = len(r.findings)
    for b in beats:
        for cue in text_cues(b):
            text, hold = cue.get("text", ""), float(cue.get("hold", 0))
            if text and hold > 0 and len(text) / hold > 17:
                r.add("default.super_speed", "needs_review", False, beat=b["id"], t=b["start"], method="plan",
                      evidence=f"planned {len(text) / hold:.1f} cps; 17 is an uncalibrated prompt, not a limit",
                      fix="check reading effort at intended size; retain deliberate fast text if it works")
        for field in text_of(b):
            for pat in STOCK:
                if field and re.search(pat, field, re.I):
                    r.add("default.stock_copy", "needs_review", False, beat=b["id"], t=b["start"], method="plan",
                          evidence=f"'{field}' matches /{pat}/", fix="does this wording serve this film? Keep it if it does")
    if "default.pace_varies" in hints and len(beats) >= 3:
        durs = [float(b["dur"]) for b in beats]
        cv = statistics.pstdev(durs) / statistics.mean(durs)
        if cv < 0.25:
            r.add("default.pace_varies", "needs_review", False, method="plan",
                  evidence=f"beat-length variation {cv:.2f}; rhythm quality is not measured",
                  fix="inspect pacing; even rhythm can be intentional")
    flagged = {f["rule"] for f in r.findings[before:]}
    for rule, what in (("default.super_speed", "all planned text cues at or under 17 cps"),
                       ("default.stock_copy", "no stock openers or filler in planned text or VO")):
        if rule not in flagged and rule not in r.overrides:
            r.add(rule, "pass", False, method="plan", evidence=what)
    words = sum(len(text_of(b)[1].split()) for b in beats)
    dur = float(r.score.get("duration", 0)) or 1
    if words / dur > 2.5:
        r.add("default.vo_budget", "needs_review", False, method="plan",
              evidence=f"{words} planned VO words in {dur:.1f}s; listen to the actual delivery")
    grid = []
    if audiomap:
        grid = audiomap.get("beats_sec") or [p["start"] for p in audiomap.get("phrases", []) if "start" in p]
    if "default.cut_on_phrase" in hints and r.score.get("lead") == "music" and grid:
        for e in events:
            if e["type"] == "cut" and not any(abs(float(e["t"]) - g) <= 2 / r.score.get("fps", 24) for g in grid):
                r.add("default.cut_on_phrase", "needs_review", False, method="plan", t=e["t"],
                      evidence="cut falls outside the suggested grid; off-grid editing can be deliberate")
        if not any(f["rule"] == "default.cut_on_phrase" for f in r.findings):
            r.add("default.cut_on_phrase", "pass", False, method="plan",
                  evidence=f"every planned cut is within 2 frames of the audiomap grid ({len(grid)} points)")


# -------------------------------------------------------------------- judged

def judged(r: Review, stage: str, sheet: str | None, strip_png: str | None):
    beats = r.score.get("beats", [])
    if stage in ("style_frames", "final"):
        r.add("judged.reel_bar", "needs_review", False, evidence=f"see {sheet}", method="inspection",
              fix="Would this go first in a senior motion designer's showreel? Name what holds it back.")
    if stage == "final":
        r.add("judged.story", "needs_review", False, method="inspection",
              evidence="the chosen telling, proposition and last beat in plan/treatment.md",
              fix="Watching as the viewer would: does the story from step 3 come through?")
    if stage in ("style_frames", "final"):
        for b in beats:
            r.add("judged.frame", "needs_review", False, beat=b["id"], t=b["start"],
                  evidence=f"job: {b.get('job', '—')} · focal: {b.get('focal', '—')} · see {sheet}",
                  method="inspection", fix="Does attention serve the intended composition, brand and beat? References apply only when chosen.")
        r.add("judged.reskin", "needs_review", False, evidence=f"see {sheet}",
              method="inspection", fix="Is this a useful subject-specific treatment or an interchangeable template? Simple title cards need not be unique.")
    if stage in ("animatic", "final"):
        for i, b in enumerate(beats):
            tr = transition(b)
            if i > 0 and (tr.get("type") != "cut" or tr.get("relationship")):
                r.add("judged.transition", "needs_review", False, beat=b["id"], t=b["start"],
                      evidence=f"declared {tr}; see transition samples",
                      method="inspection", fix="Does the actual edit preserve the intended relationship and reading?")
        r.add("judged.pacing", "needs_review", False, evidence=f"see {strip_png} against the feeling progression",
              method="inspection", fix="Does the rhythm follow the treatment? Activity is measured; good pacing is judged.")


# ---------------------------------------------------------------------- main



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
            build = float((b.get("motion") or {}).get("build", 0) or 0)
            mid = b["start"] + build + (b["dur"] - build) / 2
            samples.append({"beat": b["id"], "kind": "style (mid-hold)", "t": round(mid, 3), "path": str(p)})
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
        if integrity(r, a.video, info, delivery, fps, a.stage):
            raw, vfps = motion_strip.read_frames(a.video)
            res = motion_strip.analyse(raw, vfps)
            strip = {k: v for k, v in res.items() if k != "activity"}
            write_json(a.out / "strip.json", strip)
            motion_strip.draw(res, score, a.out / "strip.png")
            strip_png = str(a.out / "strip.png")
            settings = score.get("audio_analysis", {})
            audio = audio_check.check(a.video, settings.get("silence_db", -50), settings.get("min_silence", 0.25))
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
            footage(r, a.video, a.plan, info)

    frame_alignment(r)
    communication(r, a.stage, sheet)
    evidence(r, ledger)
    commitments(r, a.stage)
    defaults(r, load_json(a.audiomap) if a.audiomap else None, events)
    judged(r, a.stage, sheet, strip_png)

    order = {"fail": 0, "needs_review": 1, "pass": 2, "not_applicable": 3}
    r.findings.sort(key=lambda f: (not f["blocking"], order[f["status"]], f["t"] if f["t"] is not None else -1))
    critique = {
        "schema_version": 2,
        "stage": a.stage,
        "round": a.round,
        "render": str(a.video or a.stills),
        "render_sha256": render_hash,
        "plan_version": plan_version(a.plan),
        **review_summary(r.findings),
        "calibration": "defaults are not calibrated",
        "contact_sheet": sheet,
        "strip": strip_png,
        "findings": r.findings,
        "overridden": r.overridden,
        "unresolved": [],
        "accepted_limits": [],
    }
    write_json(a.out / "critique.json", critique)
    c = critique["counts"]
    print(f"{critique['verdict']}: {critique['blocking_open']} blocking open · "
          f"{c['fail']} fail · {c['needs_review']} needs_review · {c['pass']} pass → {a.out / 'critique.json'}")


if __name__ == "__main__":
    main()
