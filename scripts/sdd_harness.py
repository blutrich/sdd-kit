#!/usr/bin/env python3
"""Harness detection + path resolution shared by every sdd-kit script.

sdd-kit runs under more than one coding agent. Each harness names the same two
things differently:

  kit root      Claude Code: $CLAUDE_PLUGIN_ROOT   Codex: $PLUGIN_ROOT
  project dir   Claude Code: $CLAUDE_PROJECT_DIR   Codex: "cwd" in the hook payload

This module is the ONLY place those names appear. Everything else asks
`kit_root()`, `project_dir(payload)`, and `harness()`.

Override either explicitly (useful for vendored installs and CI):
  SDD_KIT_ROOT   absolute path to the kit
  SDD_HARNESS    claude | codex | generic  (skips detection)
"""
from __future__ import annotations

import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_KIT_FROM_FILE = os.path.dirname(_HERE)


def harness() -> str:
    """'claude', 'codex', or 'generic' (unknown / plain shell)."""
    forced = (os.environ.get("SDD_HARNESS") or "").strip().lower()
    if forced in ("claude", "codex", "generic"):
        return forced
    if os.environ.get("CLAUDE_PLUGIN_ROOT") or os.environ.get("CLAUDE_PROJECT_DIR"):
        return "claude"
    if os.environ.get("PLUGIN_ROOT") or os.environ.get("CODEX_HOME") or os.environ.get("CODEX_SANDBOX"):
        return "codex"
    return "generic"


def kit_root() -> str:
    """Where the kit is installed. Prefers explicit env, falls back to the
    location of this file (always correct for a vendored or cloned kit)."""
    for var in ("SDD_KIT_ROOT", "CLAUDE_PLUGIN_ROOT", "PLUGIN_ROOT"):
        val = os.environ.get(var)
        if val and os.path.isdir(os.path.join(val, "scripts")):
            return os.path.abspath(val)
    return _KIT_FROM_FILE


def project_dir(payload: dict | None = None) -> str:
    """The user's project directory: hook payload cwd → Claude env → cwd."""
    if payload and payload.get("cwd"):
        return payload["cwd"]
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def context_output_format() -> str:
    """How a SessionStart hook should hand context back: 'json' (the
    hookSpecificOutput.additionalContext contract) or 'text' (plain stdout).
    Both harnesses accept JSON; SDD_HOOK_FORMAT=text forces plain text for
    any harness that only reads stdout."""
    forced = (os.environ.get("SDD_HOOK_FORMAT") or "").strip().lower()
    if forced in ("json", "text"):
        return forced
    return "json"
