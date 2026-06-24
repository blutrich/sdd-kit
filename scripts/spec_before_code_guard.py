#!/usr/bin/env python3
"""PreToolUse hook — the 'spec before code' gate (Key Rule 1), deterministically.

Repo-agnostic, dependency-free. Fires before Edit/Write/MultiEdit. If the agent
is about to modify *implementation code* on a feature branch that has no
committed feature spec (specs/<branch>/requirements.md), it nudges: write the
spec first. By default this is ADVISORY (adds context, never blocks) so the
plugin is safe to drop into any repo. To make it a hard gate, set the env var
SDD_GUARD=block — then a missing spec returns 'deny' and the edit is refused.

Never touches files outside an implementation path: edits to specs/, docs,
config, tests, and markdown pass through untouched. Always fails open on any
internal error — a guard that breaks the editor is worse than no guard.

Input: the PreToolUse JSON on stdin (tool_name, tool_input.file_path, cwd).
Output (advisory): {"hookSpecificOutput": {"additionalContext": "..."}} + exit 0.
Output (block):    {"hookSpecificOutput": {"permissionDecision": "deny",
                    "permissionDecisionReason": "..."}} + exit 0.
"""
import json
import os
import re
import subprocess
import sys

# Where specs live, relative to the repo root. Default "specs". Override with
# SDD_SPECS_DIR to keep specs out of the top level, e.g. SDD_SPECS_DIR=docs/specs.
SPECS_DIR = (os.environ.get("SDD_SPECS_DIR", "specs") or "specs").strip().strip("/")

# Paths that are NOT implementation code — editing these never needs a spec.
EXEMPT_PREFIXES = (SPECS_DIR.lower() + "/", "specs/", "docs/", ".agent/", ".claude/", ".github/")
EXEMPT_SUFFIXES = (".md", ".json", ".yml", ".yaml", ".toml", ".txt", ".lock")
EXEMPT_NAMES = ("package.json", "tsconfig.json", "README.md")
# Only treat these as "implementation code".
CODE_EXTS = (".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java", ".rb", ".php", ".c", ".cpp", ".cs", ".swift", ".kt")


def git(args, cwd):
    try:
        return subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=5
        ).stdout.strip()
    except Exception:
        return ""


def is_code_path(rel: str) -> bool:
    low = rel.lower()
    if low.startswith(EXEMPT_PREFIXES) or low.endswith(EXEMPT_SUFFIXES):
        return False
    if os.path.basename(low) in EXEMPT_NAMES:
        return False
    if "test" in os.path.basename(low) or low.endswith(".test.ts") or low.endswith(".spec.ts"):
        return False
    return low.endswith(CODE_EXTS)


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0

    tool_input = data.get("tool_input", {}) or {}
    fpath = tool_input.get("file_path") or tool_input.get("filePath") or ""
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if not fpath:
        return 0

    root = git(["rev-parse", "--show-toplevel"], cwd) or cwd
    rel = os.path.relpath(fpath, root)
    if not is_code_path(rel):
        return 0

    # No Constitution at all → this isn't an SDD project; don't interfere.
    if not os.path.isfile(os.path.join(root, SPECS_DIR, "domain-spec.md")):
        return 0

    branch = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    spec_dir = os.path.join(root, SPECS_DIR, branch)
    has_spec = os.path.isfile(os.path.join(spec_dir, "requirements.md"))
    if has_spec:
        return 0  # spec exists — gate satisfied.

    reason = (
        f"SDD gate (Key Rule 1 — spec before code): about to edit '{rel}' but branch "
        f"'{branch}' has no feature spec at {SPECS_DIR}/{branch}/requirements.md. Write and "
        f"commit the spec first (/sdd-plan): requirements.md, plan.md, validation.md — "
        f"and ground any data-dependent decision in a real sample (KR12)."
    )

    # Fail closed by DEFAULT. We only reach here when the project already has a
    # Constitution, the edit targets real implementation code, and the branch has
    # no feature spec — exactly the condition SDD forbids. The kit's point is
    # enforcement, not advice, so block unless the operator explicitly downgrades.
    # SDD_GUARD=warn → advisory; SDD_GUARD=off → silent.
    mode = os.environ.get("SDD_GUARD", "block").lower()
    if mode in ("off", "0", "false", "none"):
        return 0
    if mode in ("warn", "advisory", "soft"):
        out = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": "⚠️ " + reason + " (advisory — SDD_GUARD=warn)",
            }
        }
    else:  # "block" (default) or anything unrecognized → fail closed
        out = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason
                + " (Set SDD_GUARD=warn for advisory, or SDD_GUARD=off to disable.)",
            }
        }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # fail open — never break the editor.
