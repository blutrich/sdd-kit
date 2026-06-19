---
name: sdd-key-rules
description: |
  The 14 non-negotiable rules of Spec-Driven Development. Consult whenever working under SDD — writing a spec, implementing, reviewing, or claiming a feature done — to check the work against the standing invariants.

  Use when about to claim "done", when deciding whether to edit a spec by hand, when writing a parser/schema against an external shape, or when surfacing a decision to the operator.

  Trigger keywords: key rules, definition of done, is it done, ground in real data, mock, noun-by-noun, spec drift, recommendation.
---

# SDD Key Rules

The standing invariants. They exist because each one names a failure that
recurs. Don't treat them as ceremony — each prevents a specific, expensive
mistake. Full rationale: `reference/sdd-playbook-v4.md`.

1. **Write the spec before touching code.** Always.
2. **Make all changes through the agent, not directly.** Manual edits cause
   drift between the three constitution files and between spec and code.
3. **Fresh context per feature.** Clear context before starting each feature so
   one feature's noise doesn't pollute the next.
4. **Commit the spec before implementation.** Specs are version-controlled
   artifacts, reviewable on their own.
5. **Small steps, frequent commits.** Keeps review manageable and cognitive debt
   low.
6. **Replan between every feature.** Don't skip it — that's where the
   constitution stays true.
7. **Surface open questions explicitly.** An unanswered question in the spec
   becomes a silent assumption in the code.
8. **validation.md mirrors plan.md.** Every plan item needs a corresponding
   check.
9. **The spec is living.** Update it when you learn something new
   mid-implementation.
10. **Omissions are not failures.** You will miss things. Update the spec and
    keep going.
11. **Audit the goal noun-by-noun before claiming done.** Every field/capability
    the phase goal names is a deliverable; confirm each is delivered, or
    explicitly deferred *with the operator's sign-off and a written reason*. A
    noun the goal named and quietly dropped is a gap, not a detail.
12. **Ground data-dependent decisions in real samples.** Before designing a
    parser, schema, or anything that consumes an external shape, look at the
    real shape. A plausible assumption about a format is a guess the agent will
    encode as fact. See `skills/sdd-grounding-discipline`.
13. **Prove "done" on real data, not mocks.** Green unit tests that mock both
    ends prove logic, not wiring. For anything that captures, emits, persists,
    or integrates, the bar for "done" is one real run inspected end-to-end.
    "Built and tested" ≠ "works."
14. **Interview with a recommendation, never a neutral menu.** Every decision you
    surface to the operator carries your recommended answer and a brief one-line
    *why* (one clause, not a paragraph). You have read the real code, data, and
    constitution — withholding a recommendation offloads judgment back onto the
    operator and wastes that context. In a structured tool (`AskUserQuestion`):
    recommended option **first**, label ends with `(Recommended)`, *why* in its
    description — not a `RECOMMEND:`-prefixed question, not a recommendation
    buried in a non-flagged option. In free prose: a single leading "I recommend
    X because Y."

## The two that v4 promoted to hard rules

Rules **12** and **13** were added after a real build repeatedly shipped
confidently-wrong code: technical decisions written from a *plausible* mental
model of an external system instead of its *real* shape, and "done" claimed on
green tests that mocked both ends. They are the cheapest insurance against the
most expensive class of bug. When in doubt, look at the real thing, and run it
once for real.
