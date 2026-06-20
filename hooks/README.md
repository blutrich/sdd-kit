# sdd-kit hooks

Deterministic enforcement of the SDD gates — so they fire from the harness, not
only from agent goodwill. Repo-agnostic and dependency-free (Python 3 stdlib).
All hooks **fail open**: any internal error exits 0 and never breaks your session.

| Hook | Event | What it does |
|---|---|---|
| `inject_constitution.py` | `SessionStart` | If the project has a Constitution (`specs/domain-spec.md`), injects a short pointer to it + the next unchecked roadmap phase, so the agent starts grounded. Silent when there's no Constitution. |
| `spec_before_code_guard.py` | `PreToolUse` (Edit/Write/MultiEdit) | The "spec before code" gate (Key Rule 1). **Blocks** an edit to *implementation code* on a branch with no `specs/<branch>/requirements.md`. Downgrade with `SDD_GUARD=warn`/`off`. |

## Blocking by default, downgrade when you want

The spec-before-code guard **blocks** by default — the kit's purpose is
enforcement, not advice. It refuses an edit to implementation code on a branch
with no `specs/<branch>/requirements.md`. Downgrade per shell:

```bash
export SDD_GUARD=warn   # advisory — adds a warning, never blocks
export SDD_GUARD=off    # silent — no warning, no block
```

This is safe to drop into any repo because the guard only fires on real
implementation code, on a branch with no spec, in a project that **already has a
Constitution** (`specs/domain-spec.md`). Edits to `specs/`, docs, config, tests,
and markdown always pass through, and a project that has never run
`/sdd-constitution` is never touched.

## How they load

`hooks/hooks.json` is auto-discovered when sdd-kit is installed as a plugin;
`${CLAUDE_PLUGIN_ROOT}` resolves to the plugin directory. If you've vendored the
folder instead of installing it, reference the same scripts from your project's
`.claude/settings.json` `hooks` block.
