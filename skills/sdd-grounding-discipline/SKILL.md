---
name: sdd-grounding-discipline
description: |
  Ground every data-dependent decision in a REAL sample before writing it down. Use whenever a spec or implementation will parse, store, or react to the shape of something external — a file format, an API response, a log line, a live database's columns, a third-party quota.

  Use before designing a parser, a schema, a DB migration, a mapping, or any code that consumes an external shape. This is the cheapest insurance against confidently-wrong code that passes its own tests and fails in production.

  Trigger keywords: parser, schema, format, API response, log line, DB columns, migration, fixture, real sample, ground, plausible vs real.
---

# Grounding Discipline (Key Rule 12)

A decision written from a *plausible mental model* of something external is a
guess, and the agent will faithfully encode the guess. A spec is only as true as
the reality underneath it. The code tells you what it *intends*; only the data
tells you what is *true*.

## The rule

Whenever a decision depends on the real shape of an external artifact, **verify
the real artifact first** — read the real file, call the real API, query the real
DB, grep the real log — *before* writing the decision.

## How to ground (in order of preference)

1. **Capture a real sample.** Pull one actual instance of the shape: a real API
   response body, a real row from the live DB, a real log line, the first 200
   bytes of the real file.
2. **Paste it (or its structure) into the spec** before writing the decision
   that depends on it. The fixture used in tests must match a *real* observed
   example, not an invented one.
3. **Write the decision against the observed shape**, not the imagined one.

## The brownfield trap

Reverse-engineering the *code* is not enough — verify the runtime *data*. Code
tells you what the system intends; only the running system tells you what it
actually produces. The most expensive mistakes in a brownfield build come from a
confident, wrong assumption about a format nobody actually looked at.

## Red flags that you are guessing

- "The API probably returns `{ data: [...] }`" — did you call it?
- "The log line format is roughly…" — did you grep a real one?
- "The column is likely named `created_at`" — did you describe the table?
- A test fixture you typed from memory instead of from a captured sample.

## At validation time

`validation.md` must confirm every data-dependent decision was checked against a
real sample and that the sample (or its structure) is cited in the spec. If the
feature parses an external format, the test fixtures must match a real observed
example. This is the cheapest insurance against the most expensive class of bug:
a parser/schema built against an imagined shape.
