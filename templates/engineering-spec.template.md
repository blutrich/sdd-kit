# Engineering Spec — <Project Name>

> Technology-dependent. A developer reading this should understand exactly how
> the domain spec is implemented in this stack.

## System Design
Short architectural summary: how many surfaces, how they communicate, key data
flows. Include a layered architecture diagram (even a simple ASCII one).

## Configuration
| Env var | Default | Description |
|---|---|---|
| … | … | … |
A variable not in this table is one the agent will hardcode.

## API Contract
Every endpoint: method, path, request shape, response shape, error responses.
(The underlying domain interaction lives in domain-spec.md; its REST expression
lives here.)

## Data Schemas
DB tables (columns, types, constraints, relationships), models/types,
serialization formats. Don't leave schema design to the agent — changes cascade.

## Key Pipeline / Request Lifecycle
The most important endpoint/process, step by step as actual algorithms:
computational steps, data transformations, external calls, conditional branches,
state transitions. Where domain business rules get their concrete implementation.

## Error Handling
Per failure mode: what state the system ends in, what the caller receives, what
gets logged. **Enumerate external-dependency failures explicitly** — for each
external dependency (third-party API, model/LLM provider, auth/OAuth, queue,
container/runtime, network): rate-limit / quota exhaustion / spend caps, auth
expiry, timeout/outage, malformed response. For each: what the caller sees, what
is recorded, and confirm it is **never silently swallowed**.

## Components
One subsection per major internal component. For each: input, output, algorithm
(the actual computational steps), constraints.

## Observability / Instrumentation
The seam through which the system records its own activity: the store/tables or
event stream, the collection point(s) in the pipeline, the events emitted. Three
invariants every feature inherits:
1. **Out-of-band / best-effort** — runs after the user-facing action, can never
   block/delay/fail a live path.
2. **Records facts, not fabrications** — raw observed values; don't synthesize a
   derived metric from a drifting hardcoded table; record inputs, derive once.
3. **Privacy boundary** — state what may/may not be captured; default to metadata
   (counts, flags, enums, ids), never payload bodies or sensitive content.

## Smoke Tests
4–6 named end-to-end scenarios ("submit X with Y, verify Z appears in W") — a
concrete definition of "working." Narrative, not unit tests.

## Dependencies
The exact package.json (or equivalent). Pin versions.

## Project Layout
The full directory tree with comments explaining what lives where.

## Open Questions
Unresolved engineering decisions, surfaced honestly.
