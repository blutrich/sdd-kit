#!/usr/bin/env python3
"""PreToolUse hook — the 'spec before code' gate (Key Rule 1), deterministically.

Repo-agnostic, dependency-free. Fires before Edit/Write/MultiEdit. If the agent
is about to modify *implementation code* on a branch that has no committed
feature spec, the edit is DENIED (fail-closed is the default — the kit's point
is enforcement, not advice). Downgrade with SDD_GUARD=warn (advisory context,
never blocks) or SDD_GUARD=off (silent no-op).

Spec resolution (Key Rule 1 + 4): the branch maps to a spec directory under
SPECS_DIR by, in order: the exact branch name, its last path segment (so
`spec/2026-08-11-thing` finds `specs/2026-08-11-thing/`), and the branch with
slashes slugified to dashes. The matched spec's requirements.md must also be
COMMITTED to git (KR4) — an untracked file is not an approved spec.

Never touches files outside an implementation path: edits to specs/, docs,
config, tests, and markdown pass through untouched. Always fails open on any
internal error — a guard that breaks the editor is worse than no guard.

Harness-agnostic: speaks the PreToolUse contract shared by Claude Code and
Codex. Accepts an editor payload (tool_input.file_path — Edit/Write/MultiEdit)
or a Codex apply_patch payload (tool_input.patch / .input containing
`*** Add File:` / `*** Update File:` headers) and checks every touched path.

Input: the PreToolUse JSON on stdin (tool_name, tool_input, cwd).
Output (block):    {"hookSpecificOutput": {"permissionDecision": "deny",
                    "permissionDecisionReason": "..."}} + exit 0.
Output (advisory): {"hookSpecificOutput": {"additionalContext": "..."}} + exit 0.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sdd_harness import project_dir  # noqa: E402

# Where specs live, relative to the repo root. Default "specs". Override with
# SDD_SPECS_DIR to keep specs out of the top level, e.g. SDD_SPECS_DIR=docs/specs.
SPECS_DIR = (os.environ.get("SDD_SPECS_DIR", "specs") or "specs").strip().strip("/")

# Paths that are NOT implementation code — editing these never needs a spec.
EXEMPT_PREFIXES = (SPECS_DIR.lower() + "/", "specs/", "docs/", ".agent/", ".agents/",
                   ".claude/", ".codex/", ".github/")
EXEMPT_SUFFIXES = (".md", ".json", ".yml", ".yaml", ".toml", ".txt", ".lock")
EXEMPT_NAMES = ("package.json", "tsconfig.json", "README.md")
# Only treat these as "implementation code".
CODE_EXTS = (
    ".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java", ".rb", ".php",
    ".c", ".cpp", ".cs", ".swift", ".kt",
    ".sh", ".bash", ".zsh", ".sql", ".vue", ".svelte", ".ex", ".exs",
    ".dart", ".scala", ".tf", ".lua", ".pl", ".zig", ".m", ".mm",
)

# Test files are exempt. Directory-aware + anchored basename patterns — NOT a
# naive substring match ('latest.ts' is code; 'tests/helpers.py' is a test file).
TEST_DIR_SEGMENTS = {"test", "tests", "__tests__", "spec", "specs", "testing", "e2e"}
TEST_BASENAME_RE = re.compile(
    r"^(test[_\-.]|conftest\.py$)"      # test_foo.py, test-foo.ts, test.ts, conftest.py
    r"|.*[_\-.](test|spec)\.[^.]+$"     # foo_test.go, foo-test.ts, foo.test.ts, foo.spec.ts
)


def git(args, cwd):
    try:
        return subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=5
        ).stdout.strip()
    except Exception:
        return ""


def is_test_path(rel: str) -> bool:
    low = rel.lower().replace("\\", "/")
    segments = low.split("/")[:-1]
    if any(seg in TEST_DIR_SEGMENTS for seg in segments):
        return True
    return bool(TEST_BASENAME_RE.match(os.path.basename(low)))


def is_code_path(rel: str) -> bool:
    low = rel.lower()
    if low.startswith(EXEMPT_PREFIXES) or low.endswith(EXEMPT_SUFFIXES):
        return False
    if os.path.basename(low) in EXEMPT_NAMES:
        return False
    if is_test_path(rel):
        return False
    return low.endswith(CODE_EXTS)


# Codex apply_patch payloads carry paths in patch headers, not a file_path field.
PATCH_HEADER_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+?)\s*$", re.MULTILINE)
PATCH_MOVE_RE = re.compile(r"^\*\*\* Move to: (.+?)\s*$", re.MULTILINE)


def touched_paths(tool_input: dict):
    """Every file path a tool call is about to write, across harness payload
    shapes: file_path/filePath (Claude Edit/Write, Codex Edit/Write alias),
    or the headers of an apply_patch body (Codex)."""
    single = tool_input.get("file_path") or tool_input.get("filePath")
    if single:
        return [single]
    patch = tool_input.get("patch") or tool_input.get("input") or ""
    if not isinstance(patch, str) or "*** " not in patch:
        return []
    paths = [m.group(1) for m in PATCH_HEADER_RE.finditer(patch)]
    paths += [m.group(1) for m in PATCH_MOVE_RE.finditer(patch)]
    return paths


def spec_candidates(branch: str):
    """Spec-dir names this branch may map to, most specific first (fixes the
    recurring `spec/<name>` mis-resolution: a slashed branch's last segment or
    slug now matches a flat spec dir)."""
    if not branch or branch == "HEAD":
        return []
    cands = [branch]
    if "/" in branch:
        cands.append(branch.split("/")[-1])
        cands.append(branch.replace("/", "-"))
    return cands


def resolve_spec(root: str, branch: str):
    """Return (spec_dir_name, requirements_relpath) for the first candidate
    whose requirements.md exists on disk, else (None, None)."""
    for cand in spec_candidates(branch):
        req = os.path.join(root, SPECS_DIR, cand, "requirements.md")
        if os.path.isfile(req):
            return cand, os.path.relpath(req, root)
    return None, None


def is_committed(root: str, relpath: str) -> bool:
    """True when the file has at least one commit touching it (KR4). Fails open:
    if git can't answer, treat the on-disk file as satisfying the gate."""
    out = subprocess.run(
        ["git", "log", "--oneline", "-1", "--", relpath],
        cwd=root, capture_output=True, text=True, timeout=5
    )
    if out.returncode != 0:
        return True  # git unavailable/odd state — don't block on infrastructure.
    return bool(out.stdout.strip())


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0

    tool_input = data.get("tool_input", {}) or {}
    cwd = project_dir(data)
    root = os.path.realpath(git(["rev-parse", "--show-toplevel"], cwd) or cwd)

    code_rels = []
    for fpath in touched_paths(tool_input):
        abs_path = fpath if os.path.isabs(fpath) else os.path.join(cwd, fpath)
        # realpath both sides: on macOS /var is a symlink to /private/var and a
        # naive relpath would climb out of the repo and dodge the exempt prefixes.
        rel = os.path.relpath(os.path.realpath(abs_path), root)
        if is_code_path(rel):
            code_rels.append(rel)
    if not code_rels:
        return 0
    rel = code_rels[0] + (f" (+{len(code_rels) - 1} more)" if len(code_rels) > 1 else "")

    # No Constitution at all → this isn't an SDD project; don't interfere.
    if not os.path.isfile(os.path.join(root, SPECS_DIR, "domain-spec.md")):
        return 0

    branch = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    spec_name, req_rel = resolve_spec(root, branch)

    if spec_name:
        try:
            committed = is_committed(root, req_rel)
        except Exception:
            committed = True  # fail open on infrastructure errors
        if committed:
            return 0  # spec exists and is committed — gate satisfied.
        reason = (
            f"SDD gate (Key Rule 4 — commit the spec first): branch '{branch}' has a "
            f"feature spec at {SPECS_DIR}/{spec_name}/ but requirements.md is not committed. "
            f"Commit the three spec files (requirements.md, plan.md, validation.md) "
            f"before touching implementation code."
        )
    elif branch in ("main", "master"):
        reason = (
            f"SDD gate (Key Rule 1 — spec before code): you're on '{branch}', and SDD "
            f"implements on a feature branch named after its spec dir "
            f"({SPECS_DIR}/YYYY-MM-DD-feature/ ↔ branch YYYY-MM-DD-feature). "
            f"Create the branch + spec first (/sdd-plan). For a genuine hotfix, "
            f"set SDD_GUARD=warn for this shell."
        )
    elif not branch or branch == "HEAD":
        reason = (
            f"SDD gate (Key Rule 1 — spec before code): about to edit '{rel}' but HEAD is "
            f"detached (no branch), so no feature spec can be resolved. Check out the "
            f"feature branch that matches its {SPECS_DIR}/ dir, or set SDD_GUARD=warn."
        )
    else:
        looked = ", ".join(f"{SPECS_DIR}/{c}/" for c in spec_candidates(branch))
        reason = (
            f"SDD gate (Key Rule 1 — spec before code): about to edit '{rel}' but branch "
            f"'{branch}' has no feature spec (looked in: {looked}). Write and commit the "
            f"spec first (/sdd-plan): requirements.md, plan.md, validation.md — and ground "
            f"any data-dependent decision in a real sample (KR12)."
        )

    # Fail closed by DEFAULT. We only reach here when the project already has a
    # Constitution, the edit targets real implementation code, and the branch has
    # no committed feature spec — exactly the condition SDD forbids.
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
