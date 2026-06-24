#!/usr/bin/env python3
"""SessionStart hook — inject the project's SDD Constitution into context.

Repo-agnostic and dependency-free (Python stdlib only). On every session start,
if the project has a Constitution in specs/, surface a short pointer + the next
unchecked roadmap phase so the agent starts grounded in the project agreement
instead of from zero. Stays silent (and never blocks) when there is no
Constitution yet — a project that hasn't run /sdd-constitution simply gets no
context line.

Output protocol: print a JSON object with hookSpecificOutput.additionalContext
on stdout (the SessionStart contract). Always exit 0 — a context hook must never
break a session.
"""
from __future__ import annotations  # str | None hints must not eval on Python <3.10

import json
import os
import re
import sys


def find_project_root() -> str:
    # CLAUDE_PROJECT_DIR is set by Claude Code; fall back to cwd.
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def first_unchecked_phase(roadmap_path: str) -> str | None:
    try:
        text = open(roadmap_path, encoding="utf-8").read()
    except OSError:
        return None
    # Find a heading whose section still has an unchecked "- [ ]" deliverable,
    # or a phase whose Status line isn't ✅.
    headings = list(re.finditer(r"^##\s+(.*)$", text, re.MULTILINE))
    for i, h in enumerate(headings):
        start = h.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        body = text[start:end]
        if "- [ ]" in body or ("Status" in body and "✅" not in body):
            return h.group(1).strip()
    return None


def specs_dirname() -> str:
    # Where specs live, relative to the repo root. Default "specs"; override with
    # SDD_SPECS_DIR (e.g. docs/specs) to keep specs out of the top level.
    return (os.environ.get("SDD_SPECS_DIR", "specs") or "specs").strip().strip("/")


def main() -> int:
    root = find_project_root()
    specs_rel = specs_dirname()
    specs = os.path.join(root, specs_rel)
    domain = os.path.join(specs, "domain-spec.md")
    eng = os.path.join(specs, "engineering-spec.md")
    roadmap = os.path.join(specs, "roadmap.md")

    if not os.path.isfile(domain):
        # No Constitution yet — nothing to inject. Stay silent.
        return 0

    lines = [
        f"📜 This project uses Spec-Driven Development (sdd-kit). The Constitution lives in {specs_rel}/:",
        f"  - domain-spec.md (what + rules, tech-independent){' ✓' if os.path.isfile(domain) else ''}",
        f"  - engineering-spec.md (stack, schemas, observability seam){' ✓' if os.path.isfile(eng) else ''}",
        f"  - roadmap.md (sequencing){' ✓' if os.path.isfile(roadmap) else ''}",
        "Before coding: read the relevant constitution sections; ground every data-dependent "
        "decision in a real sample (KR12); prove 'done' on real data, not mocks (KR13).",
    ]
    nxt = first_unchecked_phase(roadmap) if os.path.isfile(roadmap) else None
    if nxt:
        lines.append(f"Next roadmap phase: {nxt}")

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": "\n".join(lines),
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # A context hook must never break a session.
        sys.exit(0)
