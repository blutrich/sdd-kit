#!/usr/bin/env python3
"""Mechanical check for the spec_grounded gate (Key Rule 12).

The guardian calls spec_grounded "the most-faked gate" — and its two observable
halves are trivially checkable: a non-empty samples/ directory, and a
provenance line (the capture command + a date) near the top of every sample.
This script checks exactly that. It cannot judge whether the *decisions* in
requirements.md actually cite the samples — that stays with the reviewer — but
it removes the two silent failure modes: no samples at all, and samples pasted
from memory with no provenance.

Usage:  python3 check_grounding.py <feature-spec-dir>
Exit:   0 = pass, 1 = fail (prints each failure), 2 = bad invocation.
"""
import os
import re
import sys

PROVENANCE_RE = re.compile(
    r"(captured|provenance|via:|command:|source:)", re.IGNORECASE
)
DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
HEAD_LINES = 15  # provenance must be near the top, not buried


def check(feature_dir: str) -> int:
    if not os.path.isdir(feature_dir):
        print(f"FAIL: not a directory: {feature_dir}")
        return 2

    req = os.path.join(feature_dir, "requirements.md")
    samples = os.path.join(feature_dir, "samples")
    failures = []

    if not os.path.isfile(req):
        failures.append(f"missing {os.path.join(feature_dir, 'requirements.md')}")

    sample_files = []
    if os.path.isdir(samples):
        sample_files = [
            os.path.join(samples, f)
            for f in sorted(os.listdir(samples))
            if os.path.isfile(os.path.join(samples, f)) and not f.startswith(".")
        ]
    if not sample_files:
        failures.append(
            f"no captured samples: {samples}/ is missing or empty. "
            f"Every data-dependent decision needs a REAL captured sample (KR12) — "
            f"capture one (real API call / DB row / log line / file bytes) and commit it."
        )

    for path in sample_files:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                head = "".join(fh.readline() for _ in range(HEAD_LINES))
        except OSError as e:
            failures.append(f"unreadable sample {path}: {e}")
            continue
        if not PROVENANCE_RE.search(head):
            failures.append(
                f"{path}: no provenance line in the first {HEAD_LINES} lines. "
                f"Each sample must open with how it was captured, e.g. "
                f"'captured 2026-08-11 via: curl https://…' — a sample without "
                f"provenance is indistinguishable from one pasted from memory."
            )
        elif not DATE_RE.search(head):
            failures.append(
                f"{path}: provenance line has no capture date (YYYY-MM-DD) in the "
                f"first {HEAD_LINES} lines."
            )

    if failures:
        print(f"spec_grounded (KR12) — {len(failures)} failure(s) in {feature_dir}:")
        for f in failures:
            print(f"  ❌ {f}")
        return 1

    print(
        f"spec_grounded (KR12) — mechanical check PASS: "
        f"{len(sample_files)} sample(s) with provenance in {os.path.relpath(samples)}. "
        f"(Decision↔sample citations still need the reviewer's eye.)"
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(check(sys.argv[1]))
