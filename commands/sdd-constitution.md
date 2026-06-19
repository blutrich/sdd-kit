---
description: Write or refresh the project Constitution — domain-spec.md, engineering-spec.md, roadmap.md — through a grounded interview.
argument-hint: "[greenfield | brownfield] (default: detect)"
---

# /sdd-constitution

Produce or update the three Constitution files in `specs/`. Delegate to the
`constitution-author` agent. Read `reference/sdd-playbook-v4.md` (Part 1) and
`reference/where-does-it-go.md` first.

## Detect the mode
- **Greenfield** (no code, or `$ARGUMENTS` = greenfield): interview the operator
  with clarifying questions, each carrying a recommendation (Key Rule 14).
- **Brownfield** (existing code): reverse-engineer the constitution from README,
  issues, and code — then **verify the runtime data, not just the code** (Key
  Rule 12). Capture real samples of every external shape the system depends on.

## Produce
Write through the agent (never hand-edit), into the project's `specs/`:
- `specs/domain-spec.md` — from `templates/domain-spec.template.md`
- `specs/engineering-spec.md` — from `templates/engineering-spec.template.md`
- `specs/roadmap.md` — from `templates/roadmap.template.md`

## Gate before finishing
- Every section present; open questions listed honestly, not answered silently.
- The "Unknown is never recorded as success" invariant is stated in domain-spec.
- The observability seam + three invariants are in engineering-spec.
- Each roadmap phase has a goal AND a "What this gives users/team/system" line.
- Review with the operator before committing. Commit the constitution.
