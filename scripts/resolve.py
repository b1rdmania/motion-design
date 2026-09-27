#!/usr/bin/env python3
"""Record a review decision without overwriting the original observation."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from _common import load_json, review_summary, write_json


def resolve(critique: dict, finding_id: str, status: str, evidence: str, method: str) -> None:
    if status not in ("pass", "fail", "not_applicable") or not evidence.strip() or not method.strip():
        raise ValueError("a terminal status, inspection evidence and method are required")
    finding = next((f for f in critique["findings"] if f.get("id") == finding_id), None)
    if finding is None:
        raise ValueError(f"unknown finding {finding_id}")
    if finding["status"] != "needs_review":
        raise ValueError("only uncertain findings can be resolved; re-run checks after fixing measured failures")
    if finding.get("resolution"):
        finding.setdefault("resolution_history", []).append(finding["resolution"])
    finding["resolution"] = {"status": status, "evidence": evidence, "method": method,
                             "at": datetime.now(timezone.utc).isoformat()}
    critique.update(review_summary(critique["findings"]))


def carry(critique: dict, old: dict, old_path: str) -> int:
    """Evidence findings depend on the plan and ledger, not on the render. When the plan
    version is unchanged, an earlier decision on the same finding still holds."""
    if not old or old.get("plan_version") != critique.get("plan_version"):
        raise SystemExit("the earlier critique was made on a different plan version; nothing carried")
    done = {(f["rule"], f.get("beat"), f.get("evidence")): f["resolution"]
            for f in old.get("findings", []) if f.get("resolution") and f["rule"].startswith("evidence.")}
    n = 0
    for f in critique["findings"]:
        key = (f["rule"], f.get("beat"), f.get("evidence"))
        if f["status"] == "needs_review" and not f.get("resolution") and key in done:
            prior = done[key]
            f["resolution"] = {**prior, "method": f"{prior['method']} (carried from {old_path})"}
            n += 1
    critique.update(review_summary(critique["findings"]))
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--critique", required=True, type=Path)
    ap.add_argument("--finding")
    ap.add_argument("--status", choices=["pass", "fail", "not_applicable"])
    ap.add_argument("--evidence")
    ap.add_argument("--method", help="e.g. frame inspection, playback listening, source verification")
    ap.add_argument("--rule", help="resolve every open finding with this rule (optionally with --beat) at once; "
                                   "only when one inspection genuinely covers them all")
    ap.add_argument("--beat")
    ap.add_argument("--carry-from", type=Path, metavar="OLD_CRITIQUE",
                    help="copy decisions on evidence findings from an earlier critique of the same plan version")
    ap.add_argument("--accept-limit", metavar="TEXT",
                    help="record a limit you judged and accepted; it is listed in DELIVERY.md")
    a = ap.parse_args()
    critique = load_json(a.critique)
    if a.accept_limit:
        critique.setdefault("accepted_limits", []).append(
            {"limit": a.accept_limit, "at": datetime.now(timezone.utc).isoformat()})
        write_json(a.critique, critique)
        print(f"accepted limit recorded ({len(critique['accepted_limits'])} total)")
        return
    if a.carry_from:
        n = carry(critique, load_json(a.carry_from), str(a.carry_from))
        write_json(a.critique, critique)
        print(f"carried {n} evidence decisions from {a.carry_from}; {critique['verdict']}: "
              f"{critique['blocking_open']} blocking open")
        return
    if not (a.status and a.evidence and a.method) or not (a.finding or a.rule):
        ap.error("--finding (or --rule), --status, --evidence and --method are required "
                 "(or use --accept-limit / --carry-from)")
    ids = [a.finding] if a.finding else [
        f["id"] for f in critique["findings"]
        if f["rule"] == a.rule and (a.beat is None or f.get("beat") == a.beat)
        and f["status"] == "needs_review" and not f.get("resolution")]
    if not ids:
        ap.error("no open finding matches")
    try:
        for fid in ids:
            resolve(critique, fid, a.status, a.evidence, a.method)
    except ValueError as error:
        ap.error(str(error))
    write_json(a.critique, critique)
    print(f"{critique['verdict']}: {critique['blocking_open']} blocking open")


if __name__ == "__main__":
    main()
