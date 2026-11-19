#!/usr/bin/env python3
"""
verify_example.py

The pattern for a stage verifier. Copy it to verify_<stage>.py, point RUN_GLOB
at the stage's output directories, and replace the checks with the stage's own.

A verifier re-derives the numbers a report asserts from the primary data, tests
invariants that must hold on every row, and compares the predictions written in
DECISIONS.md before the run against the outcome. A check it cannot perform is
printed as SKIP with the reason and is never counted as a pass.

Reads   the newest results/<RUN_GLOB>/metrics.json and the primary table beside it
Writes  nothing; exits non-zero if any check fails

Usage
-----
    python3 tools/verify_example.py        (run from the stream folder)
"""

import csv
import json
import sys
from pathlib import Path

STREAM = Path(__file__).resolve().parent.parent
RUN_GLOB = "example_*"

# Predictions as written in DECISIONS.md before the run: id -> (metric, low, high).
PREDICTIONS = {}

passed, failed = [], []


def check(name, ok, detail=""):
    (passed if ok else failed).append(name)
    print("{} {}{}".format("PASS" if ok else "FAIL", name, ": " + detail if detail else ""))


def skip(name, reason):
    print("SKIP {}: {}".format(name, reason))


def main():
    runs = sorted(STREAM.glob("results/" + RUN_GLOB))
    if not runs:
        skip("all checks", "no results/{} directory yet".format(RUN_GLOB))
        return 0
    run = runs[-1]
    metrics_path = run / "metrics.json"
    if not metrics_path.exists():
        check("metrics.json present", False, str(metrics_path))
        return 1
    metrics = json.loads(metrics_path.read_text())

    # Re-derive each asserted number from the primary table, not from the report.
    table = run / "table.csv"
    if table.exists():
        with table.open(newline="") as f:
            rows = list(csv.DictReader(f))
        check("row count matches metrics", len(rows) == metrics.get("n_rows"),
              "{} rows, metrics says {}".format(len(rows), metrics.get("n_rows")))
        # Invariant example: every row falls in exactly one class.
        # check("classes partition the rows", sum(class_counts) == len(rows))
    else:
        skip("re-derivation from table.csv", "primary table absent (regenerate with the stage script)")

    for pid, (metric, low, high) in PREDICTIONS.items():
        value = metrics.get(metric)
        if value is None:
            skip(pid, "{} not in metrics.json".format(metric))
            continue
        held = low <= value <= high
        print("{} {}: {} = {} (predicted {} to {})".format(
            "HELD" if held else "FALSIFIED", pid, metric, value, low, high))

    print("{} passed, {} failed".format(len(passed), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
