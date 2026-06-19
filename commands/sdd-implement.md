---
description: Implement an approved feature spec — execute plan.md task groups with TDD, no merge yet.
argument-hint: "[feature dir, default: current branch's spec]"
---

# /sdd-implement

Execute the approved `plan.md` for the current feature. Delegate to the
`implementer` agent. **Refuse to start without a reviewed, committed feature
spec** (Key Rule 1) — if it's missing, route to `/sdd-plan`.

## Before writing code
- Confirm `requirements.md` / `plan.md` / `validation.md` exist and are committed.
- Re-check the grounding gate: every data-dependent decision cites a real sample
  (Key Rule 12). If not, stop and capture it.

## Execute
- Work through `plan.md` task groups in order. For large or sensitive areas
  (auth, billing, schema), do it group by group, committing after each (Key Rule
  5). Tests are the last group.
- **Instrumentation is part of the group that owns the behavior** — wire the
  recording/emit for a new action in that group, not at the end.
- If you discover the spec is wrong or incomplete, **update the spec through the
  agent** and keep going (Key Rules 9/10) — don't silently diverge.

## Stop conditions
- Do **not** merge. Implementation ends at "code-complete + unit-tested" — which
  is *not* the same claim as "works." Hand off to `/sdd-validate`.
- Every noun in the phase goal should now appear in the implementation (Key Rule
  11) — note any that don't.
