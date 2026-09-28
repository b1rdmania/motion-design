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
from _common import load_json, plan_version, sha256_file, effective_status, review_summary  # noqa: E402


def section(video: Path, crit_path: Path, plan: Path) -> tuple[list[str], bool]:
    crit = load_json(crit_path)
    lines = [f"## {video.name}", ""]
    if crit is None:
        return lines + [f"No critique at `{crit_path}`. Not reviewed.", ""], False
    ok = True
    problems = []
    if not video.exists():
        return lines + [f"Render `{video}` not found. Cannot match it to the critique. NOT CLEAR.", ""], False
    digest = sha256_file(video)
    if crit.get("stage") != "final":
        problems.append(f"latest critique is stage `{crit.get('stage')}`, not `final`")
    if crit.get("render_sha256") != digest:
        problems.append("critique was made on a different file (sha256 mismatch)")
    if crit.get("plan_version") != plan_version(plan):
        problems.append("plan changed after the critique; re-run check.py or record an amendment")
    findings = crit.get("findings", [])
    blocking = [f for f in findings if f["blocking"] and effective_status(f) in ("fail", "needs_review")]
    advice = [f for f in findings if not f["blocking"] and effective_status(f) == "fail"]
    judged_open = [f for f in findings if not f["blocking"] and effective_status(f) == "needs_review"]
    summary = review_summary(findings)  # Never trust stale cached counts/verdict.
    completed = [f for f in findings if f.get("resolution") and effective_status(f) != "needs_review"
                 and f["status"] == "needs_review"]
    script_passes = [f for f in findings if f["status"] == "pass"]
    if problems or blocking:
        ok = False
    lines += [f"- sha256 `{digest}`", f"- plan version `{plan_version(plan)}`",
              f"- critique `{crit_path}` (round {crit.get('round')})", ""]
    if problems:
        lines += ["**Receipt problems:**", *[f"- {p}" for p in problems], ""]
    lines.append(f"**Status:** {'clear of blocking findings' if ok else 'NOT CLEAR'}")
    lines.append("")
    lines += [f"**Current findings:** {summary['counts']}", "",
              "**Script results marked pass (scope as recorded):**", *[
                  f"- `{f['rule']}` ({f.get('method', 'script')}): {f['evidence']}" for f in script_passes], ""]
    lines += ["**Recorded reviewer decisions:**", *[
        f"- `{f['rule']}` {effective_status(f)} · {f['resolution']['method']} · {f['resolution']['evidence']}"
        for f in completed], ""] if completed else ["**Recorded reviewer decisions:** none", ""]
    if blocking:
        lines += ["**Open blocking findings:**", *[
            f"- `{f['rule']}` {effective_status(f)} · beat {f['beat']} · {f['t']}s · "
            f"{f.get('resolution', {}).get('evidence', f['evidence'])}" for f in blocking], ""]
    if advice:
        lines += ["**Defaults not met (advice):**", *[
            f"- `{f['rule']}` · beat {f['beat']} · {f['evidence']}" for f in advice], ""]
    if judged_open:
        lines += [f"**Advisory/review items not resolved:** {len(judged_open)}", *[
            f"- `{f['rule']}` · beat {f['beat']} · {f['t']}s · {f['evidence']}"
            for f in judged_open], ""]
    if crit.get("overridden"):
        lines += ["**Overridden defaults:**", *[
            f"- `{o['rule']}`: {o['reason']}" for o in crit["overridden"]], ""]
    if crit.get("accepted_limits"):
        lines += ["**Accepted limits:**", *[f"- {x['limit'] if isinstance(x, dict) else x}"
                                             for x in crit["accepted_limits"]], ""]
    for u in crit.get("unresolved", []):
        lines.append(f"- unresolved: {u}")
    return lines, ok


def provenance(plan: Path) -> list[str]:
    score = load_json(plan / "score.json", {})
    assets = load_json(plan / "assets.json", {})
    lines = ["## Provenance", ""]
    music = score.get("music") or {}
    if music:
        lines.append(f"- Music: {music.get('track', '—')} · {music.get('provenance', 'provenance not recorded')}")
    for x in assets.get("assets", []):
        lines.append(f"- {x.get('id', x.get('path'))}: {x.get('path', '')} · source {x.get('source', 'not recorded')}"
                     f" · licence {x.get('licence', 'unknown')}" + (" · sample data" if x.get("sample_data") else ""))
    for m in assets.get("missing", []):
        lines.append(f"- Missing: {m}")
    if len(lines) == 2:
        lines.append("- No music or asset provenance recorded (plan/assets.json, score.music).")
    return lines + [""]


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
        "Only the results and reviewer decisions listed below are recorded as completed. "
        "Plan calculations do not verify the render; detector matches are heuristic. "
        "Listening and visual inspection are not inferred from a cue list or a successful script. "
        "Aesthetic quality is not certified by any check.", "",
        f"Plan: `{a.plan}` · evidence ledger: `{a.plan / 'evidence.json'}` · "
        f"treatment: `{a.plan / 'treatment.md'}`", "",
    ]
    a.out.write_text("\n".join(head + body + provenance(a.plan)) + "\n")
    print(f"{'clear' if all_ok else 'NOT CLEAR'} → {a.out}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
