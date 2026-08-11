# sdd-kit hooks

Deterministic enforcement of the SDD gates — so they fire from the harness, not
only from agent goodwill. Repo-agnostic and dependency-free (Python 3 stdlib).
All hooks **fail open**: any internal error exits 0 and never breaks your session.

| Hook | Event | What it does |
|---|---|---|
| `inject_constitution.py` | `SessionStart` | If the project has a Constitution (`specs/domain-spec.md`), injects a short pointer to it + the next unchecked roadmap phase (phase-aware — a stray `- [ ]` in a Notes section is ignored), so the agent starts grounded. Silent when there's no Constitution. |
| `spec_before_code_guard.py` | `PreToolUse` (Edit/Write/MultiEdit) | The "spec before code" gate (Key Rules 1 + 4). **Blocks** an edit to *implementation code* on a branch with no **committed** feature spec. Downgrade with `SDD_GUARD=warn`/`off`. |
| `bash_write_guard.py` | `PreToolUse` (Bash) | Makes shell writes to code files (heredocs, `>`/`>>`, `tee`, `sed -i`) **visible** when the branch has no committed spec. Deliberately advisory-only — shell parsing is heuristic and must never false-positive-block — but a bypass that announces itself stops being a quiet workaround. |

## How the guard resolves the spec

The branch maps to a spec directory under `specs/` by, in order: the **exact
branch name**, its **last path segment** (`spec/2026-08-11-thing` finds
`specs/2026-08-11-thing/`), and the branch **slugified** (`/` → `-`). The
matched `requirements.md` must also be **committed** (KR 4) — an untracked spec
file does not open the gate. On `main`/`master` or a detached HEAD the guard
explains the branch contract instead of failing cryptically.

Test files are exempt via directory segments (`tests/`, `__tests__/`, `e2e/`, …)
and anchored basename patterns (`test_*`, `*_test.*`, `*.test.*`, `*.spec.*`,
`conftest.py`) — not a substring match, so `latest.ts` counts as code.

## Verifying the hooks actually loaded

The hooks fail open, so a missing `python3` or a stale plugin cache silently
disables enforcement. Run **`/sdd-doctor`** (or
`python3 scripts/sdd_doctor.py`) to check: interpreter, script health,
plugin-cache freshness, Constitution presence, `SDD_GUARD` mode, and whether
the current branch resolves to a spec.

The hook scripts have a real test suite: `python3 -m unittest discover -s tests`.

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

## Keeping specs out of the top level

By default specs live in a top-level `specs/` directory. To nest them elsewhere
(so they don't clutter the repo root), set `SDD_SPECS_DIR` per shell:

```bash
export SDD_SPECS_DIR=docs/specs   # Constitution → docs/specs/domain-spec.md, etc.
```

Both hooks resolve this env var, and the `/sdd-constitution`, `/sdd-plan`, and
router instructions resolve the same one — so spec creation and the
spec-before-code gate stay pointed at the same place. Default is `specs`; the path
is relative to the repo root. Set it in your project's `.claude/settings.json`
`env` block (or your shell profile) so it's consistent for everyone.

## How they load

`hooks/hooks.json` is auto-discovered when sdd-kit is installed as a plugin;
`${CLAUDE_PLUGIN_ROOT}` resolves to the plugin directory. If you've vendored the
folder instead of installing it, reference the same scripts from your project's
`.claude/settings.json` `hooks` block.
