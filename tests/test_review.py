"""End-to-end tests for the review scripts, using the ffmpeg-only timing fixture."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "timing"
SCRIPTS = ROOT / "scripts"

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg required")


def render(tmp: Path, name: str, shift: int = 0) -> Path:
    out = tmp / name
    cmd = [str(FIXTURE / "make_reference.sh"), str(out)]
    if shift:
        cmd += ["--shift", str(shift)]
    subprocess.run(cmd, check=True)
    return out


def review(plan: Path, video: Path, out: Path, stage: str = "final") -> dict:
    subprocess.run([sys.executable, str(SCRIPTS / "check.py"), "--plan", str(plan), "--video", str(video),
                    "--stage", stage, "--out", str(out)], check=True, capture_output=True)
    return json.loads((out / "critique.json").read_text())


def by_rule(crit: dict, rule: str) -> list[dict]:
    return [f for f in crit["findings"] if f["rule"] == rule]


def copy_plan(tmp: Path) -> Path:
    plan = tmp / "plan"
    shutil.copytree(FIXTURE, plan)
    return plan


@pytest.fixture(scope="module")
def ref(tmp_path_factory) -> Path:
    return render(tmp_path_factory.mktemp("ref"), "ref.mp4")


def test_fixture_passes_integrity_fidelity_and_sound(ref, tmp_path):
    crit = review(FIXTURE, ref, tmp_path / "r")
    for rule in ("integrity.decode", "integrity.dimensions", "integrity.fps", "integrity.duration",
                 "fidelity.cut", "fidelity.silence", "sound.clipping", "sound.loudness", "sound.true_peak"):
        found = by_rule(crit, rule)
        assert found, rule
        assert all(f["status"] == "pass" for f in found), (rule, found)
    assert crit["render_sha256"] and crit["plan_version"]


def test_late_cut_needs_review(tmp_path):
    video = render(tmp_path, "late.mp4", shift=5)
    crit = review(FIXTURE, video, tmp_path / "r", stage="animatic")
    statuses = sorted(f["status"] for f in by_rule(crit, "fidelity.cut"))
    assert statuses == ["needs_review", "pass"]
    assert crit["verdict"] == "open"


def test_override_moves_default_out_of_findings(ref, tmp_path):
    crit = review(FIXTURE, ref, tmp_path / "r")
    assert not by_rule(crit, "default.pace_varies")
    assert crit["overridden"][0]["rule"] == "default.pace_varies"


def test_fast_super_and_number_prompt_review(ref, tmp_path):
    plan = copy_plan(tmp_path)
    score = json.loads((plan / "score.json").read_text())
    score["beats"][0]["super"] = {"text": "Saves 14 hours every week on every site search", "hold": 1.0}
    (plan / "score.json").write_text(json.dumps(score))
    crit = review(plan, ref, tmp_path / "r")
    rt = by_rule(crit, "communication.reading_time_plan")[0]
    assert rt["status"] == "fail" and rt["blocking"]  # planned reading-speed gate blocks by default
    num = by_rule(crit, "evidence.number_anchored")[0]
    assert num["status"] == "needs_review" and num["blocking"]
    assert by_rule(crit, "default.super_speed")[0]["blocking"] is False


def test_metaphor_needs_review_and_unknown_claim_fails(ref, tmp_path):
    plan = copy_plan(tmp_path)
    score = json.loads((plan / "score.json").read_text())
    score["beats"][1]["proves"] = "layers"
    score["beats"][2]["proves"] = "missing"
    (plan / "score.json").write_text(json.dumps(score))
    (plan / "evidence.json").write_text(json.dumps({"claims": [
        {"id": "layers", "type": "metaphor", "limits": "does not show a site is available"}]}))
    crit = review(plan, ref, tmp_path / "r")
    assert by_rule(crit, "evidence.metaphor_wording")[0]["status"] == "needs_review"
    assert by_rule(crit, "evidence.claim_exists")[0]["status"] == "fail"


def test_stock_copy_is_advice_only(ref, tmp_path):
    plan = copy_plan(tmp_path)
    score = json.loads((plan / "score.json").read_text())
    score["beats"][1]["super"] = {"text": "Introducing the future", "hold": 2.0}
    (plan / "score.json").write_text(json.dumps(score))
    crit = review(plan, ref, tmp_path / "r")
    stock = by_rule(crit, "default.stock_copy")
    assert stock and all(not f["blocking"] for f in stock)


def test_deliver_refuses_a_critique_of_another_file(ref, tmp_path):
    review(FIXTURE, ref, tmp_path / "r")
    other = render(tmp_path, "other.mp4", shift=1)
    res = subprocess.run([sys.executable, str(SCRIPTS / "deliver.py"), "--plan", str(FIXTURE), "--video", str(other),
                          "--critique", str(tmp_path / "r" / "critique.json"), "--out", str(tmp_path / "D.md")],
                         capture_output=True, text=True)
    assert res.returncode == 1
    assert "different file" in (tmp_path / "D.md").read_text()


def test_deliver_is_not_clear_while_blocking_review_is_open(ref, tmp_path):
    review(FIXTURE, ref, tmp_path / "r")
    res = subprocess.run([sys.executable, str(SCRIPTS / "deliver.py"), "--plan", str(FIXTURE), "--video", str(ref),
                          "--critique", str(tmp_path / "r" / "critique.json"), "--out", str(tmp_path / "D.md")],
                         capture_output=True, text=True)
    assert res.returncode == 1  # sound.repeats is open until the agent resolves it
    crit_path = tmp_path / "r" / "critique.json"
    crit = json.loads(crit_path.read_text())
    for f in crit["findings"]:
        if f["blocking"] and f["status"] == "needs_review":
            f["resolution"] = {"status": "pass", "evidence": "synthetic test decision", "method": "fixture inspection"}
    crit_path.write_text(json.dumps(crit))
    res = subprocess.run([sys.executable, str(SCRIPTS / "deliver.py"), "--plan", str(FIXTURE), "--video", str(ref),
                          "--critique", str(crit_path), "--out", str(tmp_path / "D.md")], capture_output=True, text=True)
    assert res.returncode == 0, (tmp_path / "D.md").read_text()


def test_number_in_words_needs_review_not_fail(ref, tmp_path):
    plan = copy_plan(tmp_path)
    score = json.loads((plan / "score.json").read_text())
    score["beats"][1]["super"] = {"text": "seven days for a puncture.", "hold": 2.0}
    (plan / "score.json").write_text(json.dumps(score))
    crit = review(plan, ref, tmp_path / "r")
    f = by_rule(crit, "evidence.number_anchored")[0]
    assert f["status"] == "needs_review" and f["blocking"]


# ---- follow-up fixes from the first skill test (friction logs) ----

def test_reading_gate_can_be_raised_by_delivery_spec(ref, tmp_path):
    plan = copy_plan(tmp_path)
    score = json.loads((plan / "score.json").read_text())
    score["beats"][0]["super"] = {"text": "Saves hours every week on every site search", "hold": 1.5}
    score["delivery"]["max_text_cps"] = 40
    (plan / "score.json").write_text(json.dumps(score))
    crit = review(plan, ref, tmp_path / "r")
    assert by_rule(crit, "communication.reading_time_plan")[0]["status"] == "pass"


def test_frame_zero_is_always_sampled(ref, tmp_path):
    review(FIXTURE, ref, tmp_path / "r", stage="animatic")
    frames = json.loads((tmp_path / "r" / "frames" / "frames.json").read_text())["samples"]
    assert frames[0]["kind"] == "first-frame" and frames[0]["t"] == 0.0


def test_sample_claims_need_review(ref, tmp_path):
    plan = copy_plan(tmp_path)
    score = json.loads((plan / "score.json").read_text())
    score["beats"][1]["proves"] = "screen"
    (plan / "score.json").write_text(json.dumps(score))
    (plan / "evidence.json").write_text(json.dumps({"claims": [
        {"id": "screen", "type": "sample", "limits": "sample data, not a forecast"}]}))
    crit = review(plan, ref, tmp_path / "r")
    f = by_rule(crit, "evidence.sample_labelled")[0]
    assert f["status"] == "needs_review" and f["blocking"]


def test_passing_defaults_leave_a_record(ref, tmp_path):
    crit = review(FIXTURE, ref, tmp_path / "r")
    assert by_rule(crit, "default.stock_copy")[0]["status"] == "pass"
    assert by_rule(crit, "plan.frame_aligned")[0]["status"] == "pass"


def test_off_frame_beat_start_is_flagged(ref, tmp_path):
    plan = copy_plan(tmp_path)
    score = json.loads((plan / "score.json").read_text())
    score["beats"][1]["start"] = 1.51
    (plan / "score.json").write_text(json.dumps(score))
    crit = review(plan, ref, tmp_path / "r")
    assert by_rule(crit, "plan.frame_aligned")[0]["status"] == "needs_review"


def test_embedded_footage_matches_its_source(ref, tmp_path):
    plan = copy_plan(tmp_path)
    shutil.copy(ref, tmp_path / "clip.mp4")
    score = json.loads((plan / "score.json").read_text())
    score["beats"][0]["footage"] = {"src": "clip.mp4", "in": 0.0}
    score["beats"][2]["footage"] = {"src": "clip.mp4", "in": 0.0}  # wrong in point: plate 1 vs plate 3
    (plan / "score.json").write_text(json.dumps(score))
    crit = review(plan, ref, tmp_path / "r")
    results = {f["beat"]: f["status"] for f in by_rule(crit, "fidelity.footage")}
    assert results == {"b1": "pass", "b3": "needs_review"}


def test_accepted_limits_and_provenance_reach_delivery(ref, tmp_path):
    plan = copy_plan(tmp_path)
    (plan / "assets.json").write_text(json.dumps({"assets": [
        {"id": "logo", "path": "brand/logo.svg", "source": "repo: public/logo.svg", "licence": "owned"}],
        "missing": ["no brand font file"]}))
    crit_dir = tmp_path / "r"
    review(plan, ref, crit_dir)
    subprocess.run([sys.executable, str(SCRIPTS / "resolve.py"), "--critique", str(crit_dir / "critique.json"),
                    "--accept-limit", "not tested on a real phone"], check=True, capture_output=True)
    subprocess.run([sys.executable, str(SCRIPTS / "deliver.py"), "--plan", str(plan), "--video", str(ref),
                    "--critique", str(crit_dir / "critique.json"), "--out", str(tmp_path / "D.md")],
                   capture_output=True)
    text = (tmp_path / "D.md").read_text()
    assert "not tested on a real phone" in text
    assert "repo: public/logo.svg" in text and "sine 440 Hz" in text and "no brand font file" in text


def test_bass_entry_is_detected_in_low_band():
    import numpy as np
    sys.path.insert(0, str(SCRIPTS))
    import audio_check
    sr = audio_check.SR
    t = np.arange(int(sr * 3)) / sr
    x = 0.05 * np.sin(2 * np.pi * 880 * t)
    x[int(sr * 2):] += 0.3 * np.sin(2 * np.pi * 55 * t[int(sr * 2):])
    res = audio_check.analyse(np.stack([x, x], axis=1).astype(np.float32), -50, 0.25)
    assert any(abs(o - 2.0) < 0.05 for o in res["low_onsets"])
