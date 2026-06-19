# Requirements — <YYYY-MM-DD-feature-name>

> What to build and why. The agent reads this to understand intent and
> constraints.

## Scope
What this feature covers. Use tables for structured data (fields, endpoints,
content sections, states).

| Field / Endpoint / State | Detail |
|---|---|
| … | … |

### Out of Scope
- <thing the agent might naturally add that you don't want>
- <…>

Without this list, agents expand scope.

## Decisions
Explicit choices already made, as brief bullets. Every decision you don't write
here, the agent makes for itself.
- <e.g. "No client-side JS — form submits via standard HTML POST">
- <…>

## Success Criteria
What this feature is trying to achieve, as measurable goals. (e.g. "A user can
configure and launch X in under 5 minutes.") The target the implementation must
satisfy — not something the agent implements directly.

## Observability Impact
Does this feature introduce a new **observable behavior** — a new action, a new
trigger/entry point, a new delivery path, a new external/metered call, a new
failure mode, a new state? For each, state how it becomes visible to the
monitoring layer (which record/field/event, which status). A new capability the
monitoring can't see is a **blind spot, and a blind spot is not "done."** If the
feature genuinely adds nothing observable, say so in one line — deliberately.

## Failure Modes & Unknowns
For every signal this feature records, emits, or reports, state its
`unknown`/`failed` representation and confirm it is not a default that reads as a
fact. (e.g. "delivered = true *only* on a confirmed send; a refused or
unconfirmed send records `unknown`, never `delivered`." Not: "delivered defaults
to true.")

## Analytics, Events & Usage
Which events this feature fires, when, with what properties. For any **metered
external call** (LLM/model call, paid API), record the call's real
inputs/usage/outcome as facts (model, units/tokens, success/failure) — don't
fabricate a derived figure (like cost) from a hardcoded rate table; record raw
usage and derive later, or capture the authoritative number from its source.

## Context
- **Domain / tone guidance** — how content should feel, what language is
  appropriate.
- **Stack pointers** — which existing files to use as patterns.
- **Cross-references** — the specific sections of domain-spec.md and
  engineering-spec.md relevant to this feature.
