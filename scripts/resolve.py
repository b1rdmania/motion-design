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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--critique", required=True, type=Path)
    ap.add_argument("--finding")
    ap.add_argument("--status", choices=["pass", "fail", "not_applicable"])
    ap.add_argument("--evidence")
    ap.add_argument("--method", help="e.g. frame inspection, playback listening, source verification")
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
    if not (a.finding and a.status and a.evidence and a.method):
        ap.error("--finding, --status, --evidence and --method are required (or use --accept-limit)")
    try:
        resolve(critique, a.finding, a.status, a.evidence, a.method)
    except ValueError as error:
        ap.error(str(error))
    write_json(a.critique, critique)
    print(f"{critique['verdict']}: {critique['blocking_open']} blocking open")


if __name__ == "__main__":
    main()
