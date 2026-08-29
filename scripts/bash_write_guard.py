#!/usr/bin/env python3
"""PreToolUse hook (Bash) — make shell writes to implementation code VISIBLE.

The Edit/Write guard can be bypassed by writing code through the shell
(heredocs, redirects, tee, sed -i). That bypass happened in the field and then
became a documented convention — the failure mode this hook closes. It is
deliberately ADVISORY ONLY: shell command parsing is heuristic, and a guard
with false-positive denies would break normal work. Visibility is the goal —
a bypass that announces itself stops being a quiet workaround.

Fires only when the same conditions as the main guard hold: the project has a
Constitution and the current branch resolves to no committed feature spec.
Respects SDD_GUARD=off. Always fails open.
"""
import json
import os
import re
import sys

# Reuse the main guard's logic — same dir, same interpreter invocation.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spec_before_code_guard import (  # noqa: E402
    SPECS_DIR, CODE_EXTS, git, is_code_path, resolve_spec, is_committed,
)
from sdd_harness import project_dir  # noqa: E402

# Shell constructs that write to a file: >, >>, tee [-a], sed -i, and heredocs
# piped/redirected to a target. We look for any code-extension path that appears
# as a plausible write target anywhere in the command.
WRITE_HINT_RE = re.compile(
    r"(?:>>?|\btee\b(?:\s+-a)?|\bsed\b[^|;&]*-i(?:\S*)?|\bdd\b[^|;&]*\bof=)"
)
EXT_ALT = "|".join(ext.lstrip(".") for ext in CODE_EXTS)
TARGET_RE = re.compile(r"""['"]?([\w@./\\-]+\.(?:%s))['"]?""" % EXT_ALT)


def find_write_targets(command: str):
    """Heuristic: if the command contains a write construct, collect every
    code-file path mentioned in it (conservative superset — advisory only)."""
    if not WRITE_HINT_RE.search(command) and "<<" not in command:
        return []
    return [m.group(1) for m in TARGET_RE.finditer(command)]


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0

    command = (data.get("tool_input") or {}).get("command") or ""
    if not command:
        return 0

    mode = os.environ.get("SDD_GUARD", "block").lower()
    if mode in ("off", "0", "false", "none"):
        return 0

    cwd = project_dir(data)
    root = git(["rev-parse", "--show-toplevel"], cwd) or cwd

    # Only relevant in an SDD project.
    if not os.path.isfile(os.path.join(root, SPECS_DIR, "domain-spec.md")):
        return 0

    targets = [t for t in find_write_targets(command) if is_code_path(t)]
    if not targets:
        return 0

    # If the branch has a committed spec, shell writes are as legitimate as
    # editor writes — stay silent.
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    spec_name, req_rel = resolve_spec(root, branch)
    if spec_name:
        try:
            if is_committed(root, req_rel):
                return 0
        except Exception:
            return 0

    shown = ", ".join(targets[:3]) + ("…" if len(targets) > 3 else "")
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                f"⚠️ SDD gate (Key Rule 1): this Bash command appears to write "
                f"implementation code ({shown}) on branch '{branch}', which has no "
                f"committed feature spec. Shell writes are subject to the same "
                f"spec-before-code rule as Edit/Write — do not use the shell to "
                f"route around the gate. Write the spec first (/sdd-plan)."
            ),
        }
    }))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # fail open — never break the shell.
