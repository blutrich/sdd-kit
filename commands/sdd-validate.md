---
description: Prove a feature is done — run validation.md including a real-data end-to-end check and failure/unknown verification.
argument-hint: "[feature dir, default: current branch's spec]"
---

# /sdd-validate

Run the feature's `validation.md` as an executable checklist and decide whether
the Definition of Done is truly met. Delegate to the `validator` agent, then have
the `reviewer` agent do an independent architect-level pass.

## Run, in order
1. **Automated tests + typecheck** — top-level commands must pass. Confirm **at
   least one test exercises real collaborators** (doesn't mock both ends) (Key
   Rule 13).
2. **Grounding check** — every data-dependent decision was verified against a
   real sample, and the sample/structure is cited.
3. **Manual checks** — specific behaviors a human confirms in the running app.
4. **End-to-end on real data** — trigger the real behavior, inspect the real
   artifact it produced (the live DB row, the event, the file). Capture the
   evidence. Green tests are necessary but not sufficient.
5. **Analytics & observability verification** — each specified event fires with
   the right properties; the Observability Impact is actually recorded; spot-check
   the privacy boundary (metadata only).
6. **Failure & unknown verification** — force each failure path; confirm it
   records `unknown`/`failed` and does **not** read as success/empty/delivered.

## Verdict
- **Noun-by-noun (Key Rule 11):** every noun in the phase goal is delivered, or
  explicitly deferred with the operator's sign-off and a written reason.
- Pass only if the one-sentence Definition of Done holds. If it doesn't, say what
  failed with the evidence — don't soften it.

## Final gate — hand off to a fresh `sdd-guardian` (do NOT skip)
The validator that ran the checklist must not also sign off on it — that's
self-review. Spawn the **`sdd-guardian`** agent as an independent, fresh-context
final checkpoint. It re-checks every gate in `config/workflow.json` adversarially
and returns a single **GO / NO-GO**. A single failed gate is NO-GO. Only on a GO
verdict does the feature merge.
