---
description: Verify sdd-kit is installed, loaded, and enforceable in this project — interpreter, hook scripts, plugin-cache freshness, Constitution, guard mode, and the branch↔spec contract.
argument-hint: "[project dir, default: cwd]"
---

# /sdd-doctor

The hooks fail **open** by design — a guard that breaks the editor is worse
than no guard. The cost of that choice: a missing `python3`, a stale plugin
cache, or a broken script produces a kit that *looks* installed and enforces
nothing. This command makes that state visible.

## Run

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sdd_doctor.py" "$PWD"
```

(If `CLAUDE_PLUGIN_ROOT` is not set in your context, locate the kit first: the
vendored copy at `.claude/skills/sdd-kit/`, or the marketplace cache under
`~/.claude/plugins/cache/sdd-kit/sdd-kit/<version>/`.)

## Report

Relay the doctor's output to the operator verbatim (it is already formatted),
then, for each ❌ line, state the one-line fix:

- **python3 missing / too old** → install Python ≥ 3.9 on PATH.
- **script broken** → the kit copy is corrupted; reinstall or re-pull.
- **stale plugin cache** → `/plugin update sdd-kit`.
- **no Constitution** → the kit is inert here; run `/sdd-constitution`.
- **branch resolves to no spec** → run `/sdd-plan`, or rename the branch to
  match its spec dir (flat `YYYY-MM-DD-feature` names).
- **SDD_GUARD=off/warn** → not an error, but say plainly that enforcement is
  downgraded in this shell.

Do not soften a ❌ into advice — the whole point of the doctor is that silent
failure becomes loud.
