---
description: Spec the next roadmap feature — produce requirements.md, plan.md, validation.md through a grounded interview before any code.
argument-hint: "[feature name or roadmap phase]"
---

# /sdd-plan

Create the feature spec for `$ARGUMENTS` (or the next unchecked roadmap phase)
before any implementation. Delegate to the `feature-planner` agent. Read
`reference/sdd-playbook-v4.md` (Part 2) first.

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
  external shape, capture a real sample and cite it in the spec *before* writing
  the decision. See `skills/sdd-grounding-discipline`.
- **Recommendation per question (Key Rule 14).** Never a neutral menu.
- Review all three files with the operator, then **commit the spec before
  implementation** (Key Rule 4). No code yet.
