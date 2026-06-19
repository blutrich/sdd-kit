# sdd-kit hooks

Deterministic enforcement of the SDD gates — so they fire from the harness, not
only from agent goodwill. Repo-agnostic and dependency-free (Python 3 stdlib).
All hooks **fail open**: any internal error exits 0 and never breaks your session.

| Hook | Event | What it does |
|---|---|---|
| `inject_constitution.py` | `SessionStart` | If the project has a Constitution (`specs/domain-spec.md`), injects a short pointer to it + the next unchecked roadmap phase, so the agent starts grounded. Silent when there's no Constitution. |
| `spec_before_code_guard.py` | `PreToolUse` (Edit/Write/MultiEdit) | The "spec before code" gate (Key Rule 1). When about to edit *implementation code* on a branch with no `specs/<branch>/requirements.md`, it nudges you to write the spec first. |

## Advisory by default, blocking when you want it

The spec-before-code guard is **advisory** out of the box (it adds a warning to
context, never blocks) so the plugin is safe to drop into any repo. To make it a
hard gate that refuses code edits until a spec exists:

```bash
export SDD_GUARD=block
```

It only ever considers real implementation code on a branch of a project that
*already* has a Constitution — edits to `specs/`, docs, config, tests, and
markdown always pass through, and a project that has never run
`/sdd-constitution` is never touched.

## How they load

`hooks/hooks.json` is auto-discovered when sdd-kit is installed as a plugin;
`${CLAUDE_PLUGIN_ROOT}` resolves to the plugin directory. If you've vendored the
folder instead of installing it, reference the same scripts from your project's
`.claude/settings.json` `hooks` block.
