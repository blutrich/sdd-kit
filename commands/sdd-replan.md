---
description: Close the loop after a merge — update the constitution, roadmap, process, and skills before the next feature.
argument-hint: "[just-merged feature dir]"
---

# /sdd-replan

After merging a feature, replan before starting the next one (Key Rule 6).
Delegate to the `replanner` agent. Own branch; small changes only.

## Cover
- **Constitution updates** — new decisions made during the feature? Write them
  into `domain-spec.md` / `engineering-spec.md`. **New facts about an external
  system's real shape** (a format, an API quirk, a quota) — record them so the
  next feature doesn't re-guess (this is the durable payoff of Key Rule 12).
- **Roadmap updates** — does the next planned phase still make sense? Should
  adjacent phases be combined or split? Re-check each phase still has its goal +
  "What this gives…" line.
- **Process improvements** — is something repetitive? Can it become a skill?
  (Don't build skills too early — only after real, repeated friction.)

## Rules
- Make all edits through the agent so the three constitution files stay
  consistent (Key Rule 2).
- **Small changes:** implement in the replan branch. **Large changes:** schedule
  as a new roadmap phase — don't implement during replanning.
- End by confirming the "Starting a feature" checklist is green for the next
  loop.
