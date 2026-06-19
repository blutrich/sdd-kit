---
name: sdd-observability-invariants
description: |
  The observability discipline for Spec-Driven Development — the seam through which a system records its own activity, and the standing invariants every feature inherits. Use when designing instrumentation, adding a new action/path/external call, or deciding how a system answers "did this happen, and did it succeed?".

  Use whenever a feature introduces a new observable behavior, a metered external call, a new failure mode, or a new state — and whenever you might record a missing/failed result as success.

  Trigger keywords: observability, instrumentation, telemetry, metrics, unknown vs success, blind spot, monitoring, metered call, usage, privacy boundary.
---

# Observability Invariants

A failure that leaves no trace is invisible by construction, and invisible
failures are the most expensive kind. Observability is not a dashboard you add
later — it is a seam each feature plugs into on purpose.

## The seam (designed once, in engineering-spec.md)

Describe where the system records its own activity: the store/tables or event
stream, the collection point(s) in the pipeline, and the events emitted. Every
feature's "Observability Impact" (in `requirements.md`) hooks into this seam.

## The three invariants every feature inherits

1. **Out-of-band / best-effort.** Instrumentation runs *after* the user-facing
   action and is wrapped so it can never block, delay, or fail a live path.
   Telemetry that can take down the thing it measures is worse than no telemetry.
2. **Records facts, not fabrications.** Record raw, observed values (counts,
   outcomes, usage). Do not synthesize a derived metric from a hardcoded table
   that drifts (e.g. computing a dollar cost from a per-unit price list when the
   raw inputs are what you actually have) — record the inputs and derive later in
   one place, or capture the authoritative figure from its real source.
3. **What may be recorded (privacy boundary).** State plainly what
   instrumentation may and may not capture — especially for personal, clinical,
   or otherwise sensitive data. Default to metadata (counts, flags, enums,
   identifiers) and never payload bodies or sensitive content.

## The standing invariant: Unknown is never recorded as success

Make this an explicit business rule (it belongs in `domain-spec.md`). Every
recorded or reported signal must have an explicit `unknown` / `failed`
representation, and a missing, errored, timed-out, refused, or unverifiable
signal must be recorded as such — never collapsed into `ok` / `empty` / `done` /
`delivered`.

> "Couldn't do it" must never read as "did it."

This is violated constantly: a default of `0`, `[]`, `false`, or `"success"`
standing in for "we don't actually know" is the single most common way a system
lies to its operators. Name it once in the domain spec so every feature inherits
it; operationalize it per feature in the `Failure Modes & Unknowns` section of
`requirements.md`; and force every failure/unknown path at validation time
(`validation.md`) to confirm it records `unknown`/`failed` and does not show as
success.

## Per-feature counterpart

A new capability the monitoring layer cannot see is a **blind spot, and a blind
spot is not "done."** Each feature's `requirements.md` Observability Impact
section makes the feature plug into the seam on purpose rather than by luck.
Wiring observability in *last* is how it gets dropped — the recording/emit for an
action is a step *in the task group that owns the action*, not a bolt-on.
