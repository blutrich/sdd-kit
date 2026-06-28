# Validation — <YYYY-MM-DD-feature-name>

> How to know it's done. Executable — both you and the agent should be able to
> run through this checklist. Mirrors plan.md almost point for point: every plan
> item needs a corresponding check (target 75%+ tracing back to plan/requirements).

## Grounding Evidence
- [ ] Every data-dependent decision was checked against a **real** sample, and
      the sample (or its structure) is cited in the spec.
- [ ] Test fixtures match a real observed example, not an invented one.

## Automated Tests
Top-level commands that must pass:
- [ ] `<test command>` (e.g. `npm test`)
- [ ] `<typecheck command>` (e.g. `npm run typecheck`)

Specific test cases (each states exactly what it asserts):
- [ ] <assertion>
- [ ] **Cross-feature smoke test** (required when "Services I modify" is non-empty): at least one test instantiates the modified service _and_ a real caller together — no mocks between them — and asserts the end-to-end result. This is what catches silent caller-wiring breaks when a signature changes.
- [ ] **At least one test exercises real collaborators — doesn't mock both
      ends** — runs through the real store/parser/file/adapter (in-memory or
      fixture-backed is fine) and asserts the result persists and reads back.

## Manual Checks
Things a human verifies by actually using the running app. Be specific:
- [ ] "Submitting without required fields is prevented" (not "validation works").
- [ ] …

## End-to-End on Real Data
Required for any feature that captures, emits, persists, or integrates.
- [ ] Trigger the real behavior and inspect the real artifact it produced (the
      row in the live DB, the event in the stream, the file on disk). Capture
      what you observed. Green tests are necessary but not sufficient.

## Analytics & Observability Verification
- [ ] Each specified event fires correctly, at the right moment, with the right
      properties.
- [ ] Each item in the requirements **Observability Impact** is actually
      recorded (mirror it point for point).
- [ ] Spot-check the privacy boundary (metadata only, no sensitive payloads).

## Failure & Unknown Verification
- [ ] For each signal in **Failure Modes & Unknowns**, force the failure/unknown
      path and confirm it records `unknown`/`failed` and is **not** silently
      recorded as success/empty (e.g. a refused send does not show as
      "delivered").

## Quality / Tone Check
- [ ] No placeholder text, correct tone, no leftover debug code / `console.log`.

## Definition of Done
> All automated tests pass (including at least one that doesn't mock both ends);
> every noun in the phase goal is delivered or explicitly deferred with sign-off;
> the feature is proven end-to-end against the real running system at least once
> and the evidence captured; all manual checks confirmed; branch rebased cleanly
> onto main with no leftover TODOs.
