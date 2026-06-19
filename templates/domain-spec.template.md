# Domain Spec — <Project Name>

> Technology-independent. A developer reading this should understand the domain
> completely without knowing the tech stack. Decide placement with one question:
> technology-independent → here; technology-dependent → engineering-spec.md.

## Overview
What the system actually does, as a numbered list of concrete functions
(registers X, processes Y, returns Z, tracks W). Not a tagline.

## Motivation
The specific problems this solves. Name the gaps explicitly — what breaks today,
what fails silently, what is ad hoc. Three named gaps beat a paragraph.

## Core Workflow / Lifecycle
The single most important section. Diagram/state-machine of the primary flow:
every state, every trigger that causes a transition, every edge case (timeouts,
failures, recoveries). Describe domain interactions in plain language (what
actors do, what the system returns) — their REST expression belongs in
engineering-spec.md.

## Observable Lifecycle
For each state transition and especially each **failure** path: is it observable
— can the system later answer "did this happen, and did it succeed?" A failure
that leaves no trace is invisible by construction. Declare which transitions
*must* be observable so a downstream phase can't silently skip them.

## State / Status Definitions
| State | Trigger (what causes entry) | Meaning | What's Next |
|---|---|---|---|
| … | … | … | … |

## Business Rules and Conditions
The logic that defines correct behavior, as domain rules independent of
implementation. (e.g. "If confidence ≥ 0.6 → confirmed. 0.4–0.59 → uncertain.
< 0.4 → excluded.") These are the rules the algorithms must satisfy.

## Unknown Is Never Recorded as Success (standing invariant)
Every recorded or reported signal must have an explicit `unknown`/`failed`
representation. A missing, errored, timed-out, refused, or unverifiable signal is
recorded as such — never collapsed into `ok`/`empty`/`done`/`delivered`.
"Couldn't do it" must never read as "did it." Named once here so every feature
inherits it.

## Stakeholder Voices
Named personas with specific concerns (Engineering wants X, Product wants Y,
Marketing wants Z) — prevents optimizing for the wrong goal.

## What Success Looks Like
Concrete definition + top-line KPIs (technology-independent business metrics).
(e.g. "80% complete a study without contacting support.")

## Open Questions
Unresolved domain decisions, listed honestly. If you don't write them here, the
agent answers them silently in code.

## Heritage / Inspiration (optional)
If inspired by something well-known, say so — enormous context at low cost.
