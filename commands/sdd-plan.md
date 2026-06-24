---
description: Spec the next roadmap feature — produce requirements.md, plan.md, validation.md through a grounded interview before any code.
argument-hint: "[feature name or roadmap phase]"
---

# /sdd-plan

Create the feature spec for `$ARGUMENTS` (or the next unchecked roadmap phase)
before any implementation. Delegate to the `feature-planner` agent. Read
`reference/sdd-playbook-v4.md` (Part 2) first.

## Spec location
Specs live in `${SDD_SPECS_DIR:-specs}`. Run `echo ${SDD_SPECS_DIR:-specs}` once
and treat every `specs/…` path below as relative to that directory (default
`specs/`). The hooks resolve the same env var, so honoring it keeps spec creation
and the spec-before-code gate pointed at the same place.

## Start clean
Fresh context (Key Rule 3). Confirm the previous feature branch is merged and the
constitution is up to date. Create the spec dir + branch:
`specs/YYYY-MM-DD-feature-name/` on branch `YYYY-MM-DD-feature-name`.

## Interview, then write three files (from templates/)
- `requirements.md` — scope (+ explicit Out of Scope), decisions, success
  criteria, **Observability Impact**, **Failure Modes & Unknowns**, analytics.
- `plan.md` — numbered task groups (Database → Components → Page&Route →
  Navigation → Tests). Instrumentation lives in the group that owns the behavior.
- `validation.md` — mirrors plan.md; grounding evidence, automated tests (≥1 not
  mocking both ends), manual checks, end-to-end-on-real-data, failure/unknown
  verification, Definition of Done.

## Hard gates
- **Ground first (Key Rule 12).** If the feature parses/stores/reacts to any
  external shape, capture a real sample **to a committed file** under
  `specs/<feature>/samples/` and cite the capture command in requirements.md
  *before* writing the decision. See `skills/sdd-grounding-discipline`.
- **Enumerate deliverables (Key Rule 11).** requirements.md lists each noun in
  the phase goal as an explicit deliverable checklist — the guardian checks that
  list, not re-tokenized prose.
- **Recommendation per question (Key Rule 14).** Never a neutral menu.

## Exit gate — independent plan review (before any code)
Hand the three files to a fresh **`plan-gap-reviewer`** (it does NOT see your
rationale). It hunts for ungrounded decisions, missing edge cases/states, dropped
observability, scope drift, and validation↔plan mismatches *while they're still
cheap to fix*. On **REVISE**, fix the named gaps in the spec and re-review; only on
**PROCEED** do you continue. Then review with the operator and **commit the spec
before implementation** (Key Rule 4). No code yet.
