---
name: sdd-router
description: |
  THE ENTRY POINT FOR SPEC-DRIVEN DEVELOPMENT. Activate this skill whenever the user wants to build, plan, spec, implement, validate, or replan a feature under Spec-Driven Development — or whenever the project has a specs/ directory with a Constitution.

  Use when the user says: write a spec, plan a feature, start the constitution, implement the plan, validate / prove it's done, replan, "what's next on the roadmap", or describes a feature to build in a project that uses SDD.

  Trigger keywords: spec, sdd, constitution, domain-spec, engineering-spec, roadmap, plan a feature, requirements, validation, implement, replan, ground in real data, definition of done.

  CRITICAL: Route to the correct SDD phase and run it. Fail closed on ambiguity — never start coding without an approved spec.
---

# SDD Router

The brain of `sdd-kit`. Route a request to the right phase of the Spec-Driven
Development cycle, then hand off to that phase's command/agent. The full method
is in `reference/sdd-playbook-v4.md`; the content→file map is in
`reference/where-does-it-go.md`. Read them when a decision is unclear.

## 0. Orient before routing

Read the project's `specs/` directory first:
- Is there a Constitution (`specs/domain-spec.md`, `engineering-spec.md`,
  `roadmap.md`)? If **no** → the only valid first move is the Constitution.
- What is the next unchecked phase in `roadmap.md`?
- Is there an in-flight `specs/YYYY-MM-DD-feature-name/` (the three feature
  files exist but code isn't merged)? If so, continue it — don't start a new one.

## 1. Intent routing

Route on the first matching signal. **ERROR/grounding-doubt always wins.**

| Priority | Signal | Phase | Hand off to |
|---|---|---|---|
| 1 | No Constitution yet, or "start/refresh the constitution", domain/stack/roadmap changes | CONSTITUTION | `/sdd-constitution` → `constitution-author` |
| 2 | "plan a feature", "spec X", "what's next", a new feature description | PLAN | `/sdd-plan` → `feature-planner` → `plan-gap-reviewer` (fresh-eyes gate) |
| 3 | "implement", "build the plan", an approved feature spec exists | IMPLEMENT | `/sdd-implement` → `implementer` |
| 4 | "validate", "is it done", "prove it works" | VALIDATE | `/sdd-validate` → `validator` + `reviewer` → `sdd-guardian` (GO/NO-GO) |
| 5 | "replan", a feature just merged | REPLAN | `/sdd-replan` → `replanner` |

## 2. Fail-closed gates (the whole point)

Refuse to advance and say why when:
- **No approved spec → no code.** If asked to implement without the three
  feature files reviewed, route to PLAN first (Key Rule 1).
- **Ungrounded data decision.** If the work parses/stores/reacts to an external
  shape (file format, API response, log line, live DB columns) and no real
  sample is captured and cited in the spec, stop and capture it first (Key Rule
  12). See `skills/sdd-grounding-discipline`.
- **"Done" claimed on mocks.** Don't accept completion without at least one test
  that doesn't mock both ends and one real-data end-to-end check (Key Rule 13).
- **A goal noun silently dropped.** At done, every noun in the phase goal must be
  delivered or explicitly deferred with the operator's sign-off (Key Rule 11).

## 3. How to ask

Every question you surface to the operator carries your recommended answer and a
one-line *why* (Key Rule 14). In `AskUserQuestion`, put the recommended option
**first**, end its label with `(Recommended)`, and the *why* in its description —
never a neutral menu, never a `RECOMMEND:`-prefixed question string.

## 4. Never bypass

Do not use Claude Code's native plan mode for SDD work — this kit owns planning,
so the spec artifacts, grounding gate, and validation actually get written. A
plan that lives only in chat is a plan that drifts.
