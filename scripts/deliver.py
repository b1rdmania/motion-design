#!/usr/bin/env python3
"""Write DELIVERY.md for a finished render. Refuses to call a render clean when the
latest final critique does not match the file or the plan, or when blocking findings
are still open. It never claims quality; it lists what was checked and what was not.

    python3 deliver.py --plan plan/ --video renders/final.mp4 --critique review/final-r2/critique.json \
        [--also renders/final-phone.mp4:review/final-phone-r1/critique.json] --out DELIVERY.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import load_json, plan_version, sha256_file  # noqa: E402


def section(video: Path, crit_path: Path, plan: Path) -> tuple[list[str], bool]:
    crit = load_json(crit_path)
    lines = [f"## {video.name}", ""]
    if crit is None:
        return lines + [f"No critique at `{crit_path}`. Not reviewed.", ""], False
    digest = sha256_file(video)
    ok = True
    problems = []
    if crit.get("stage") != "final":
        problems.append(f"latest critique is stage `{crit.get('stage')}`, not `final`")
    if crit.get("render_sha256") != digest:
        problems.append("critique was made on a different file (sha256 mismatch)")
    if crit.get("plan_version") != plan_version(plan):
        problems.append("plan changed after the critique; re-run check.py or record an amendment")
    findings = crit.get("findings", [])
    blocking = [f for f in findings if f["blocking"] and f["status"] in ("fail", "needs_review")]
    advice = [f for f in findings if not f["blocking"] and f["status"] == "fail"]
    judged_open = [f for f in findings if not f["blocking"] and f["status"] == "needs_review"]
    if problems or blocking:
        ok = False
    lines += [f"- sha256 `{digest}`", f"- plan version `{plan_version(plan)}`",
              f"- critique `{crit_path}` (round {crit.get('round')})", ""]
    if problems:
        lines += ["**Receipt problems:**", *[f"- {p}" for p in problems], ""]
    lines.append(f"**Status:** {'clear of blocking findings' if ok else 'NOT CLEAR'}")
    lines.append("")
    if blocking:
        lines += ["**Open blocking findings:**", *[
            f"- `{f['rule']}` {f['status']} · beat {f['beat']} · {f['t']}s · {f['evidence']}" for f in blocking], ""]
    if advice:
        lines += ["**Defaults not met (advice):**", *[
            f"- `{f['rule']}` · beat {f['beat']} · {f['evidence']}" for f in advice], ""]
    if judged_open:
        lines += [f"**Judged items not resolved:** {len(judged_open)}", ""]
    if crit.get("overridden"):
        lines += ["**Overridden defaults:**", *[
            f"- `{o['rule']}`: {o['reason']}" for o in crit["overridden"]], ""]
    for u in crit.get("unresolved", []):
        lines.append(f"- unresolved: {u}")
    return lines, ok


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--video", type=Path, required=True)
    ap.add_argument("--critique", type=Path, required=True)
    ap.add_argument("--also", action="append", default=[], help="extra VIDEO:CRITIQUE pairs")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    pairs = [(a.video, a.critique)] + [tuple(Path(x) for x in p.split(":", 1)) for p in a.also]
    body, all_ok = [], True
    for v, c in pairs:
        lines, ok = section(v, c, a.plan)
        body += lines
        all_ok = all_ok and ok
    score = load_json(a.plan / "score.json", {})
    head = [
        f"# Delivery: {score.get('title', a.plan.resolve().parent.name)}", "",
        "Checked by script: decode, dimensions, fps, duration, reading time, evidence ids, loudness, "
        "true peak, clipping, planned cuts and silences. Judged by inspecting frames: legibility at "
        "viewing size, brand, commitments, transitions, pacing. Aesthetic quality is not certified "
        "by any check.", "",
        f"Plan: `{a.plan}` · evidence ledger: `{a.plan / 'evidence.json'}` · "
        f"treatment: `{a.plan / 'treatment.md'}`", "",
    ]
    a.out.write_text("\n".join(head + body) + "\n")
    print(f"{'clear' if all_ok else 'NOT CLEAR'} → {a.out}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
