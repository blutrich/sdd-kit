# Spec-Driven Development — Complete Playbook (v4)

> Canonical reference for `sdd-kit`. The agents, commands, and skills in this
> plugin operationalize this document. When they and this disagree, this wins.

## What this is

Spec-Driven Development (SDD) is a workflow for building software with AI coding
agents. Instead of describing what you want in a prompt and hoping (vibe
coding), you write structured markdown specifications **before** the agent
writes a single line of code. The spec is the brain. The agent is the muscle.
Your role shifts from writing code to writing clear specifications and reviewing
the agent's output as an architect or supervisor.

## Why it works

- **Small spec changes produce large code changes.** One sentence — "use SQLite
  instead of PostgreSQL" — might affect hundreds of lines.
- **Specs solve context decay.** Agents are stateless; every session starts from
  zero. Specs persist across sessions, agents, and teammates.
- **Specs improve intent fidelity.** Every decision you don't write down, the
  agent makes on its own — and usually wrong.
- **Grounded specs beat plausible specs.** A decision written from a plausible
  mental model of something external (a file format, an API shape, a log line, a
  DB's real contents) is a guess the agent will faithfully encode. Verify the
  real artifact before writing the decision. The code tells you what it
  *intends*; only the data tells you what is *true*.

## The SDD cycle

```
PROJECT CONSTITUTION  (domain-spec.md / engineering-spec.md / roadmap.md)
        │  written once, updated often
        ▼
FEATURE LOOP  1. PLAN → 2. IMPLEMENT → 3. VALIDATE  (loops back)
        ▼
REPLAN  update constitution, roadmap, process, skills → next feature loop
```

---

## Part 1: The Constitution

The project-level agreement between you, your teammates, and the agent. Lives in
`specs/` as three files. The split is decided by one question: **is this
decision technology-independent or technology-dependent?**

Never edit the three files directly — make all changes through the agent so they
stay consistent. **Greenfield:** write it first, in a clarifying interview.
**Brownfield:** point the agent at existing artifacts to reverse-engineer it —
but verify the runtime *data*, not just the code.

### domain-spec.md (technology-independent product/domain spec)

Everything that defines what the product is and how it behaves, independent of
tech choices. Sections: **Overview** (numbered concrete functions), **Motivation**
(named gaps), **Core Workflow / Lifecycle** (the single most important section —
states, triggers, edge cases; the map everything is built on), **Observable
Lifecycle** (which transitions/failures must be observable), **State/Status
Definitions** (table: State | Trigger | Meaning | What's Next), **Business Rules
and Conditions** (the rules the algorithms must satisfy), **Unknown is never
recorded as success** (standing invariant), **Stakeholder Voices**, **What
Success Looks Like** (top-line KPIs, technology-independent), **Open Questions**,
**Heritage / Inspiration**.

### engineering-spec.md (technology-dependent)

Everything specific to your technology choices. Sections: **System Design**
(architecture summary + diagram), **Configuration** (every env var: name,
default, description), **API Contract** (every endpoint: method, path, shapes,
errors), **Data Schemas** (DB tables, types, models), **Key Pipeline / Request
Lifecycle** (the most important process as concrete steps), **Error Handling**
(per failure mode — and **enumerate external-dependency failures explicitly**:
rate-limit / quota / spend caps, auth expiry, timeout/outage, malformed response;
for each, what the caller sees and what's recorded, never silently swallowed),
**Components** (per component: input, output, algorithm, constraints),
**Observability / Instrumentation** (the seam + three invariants — see
`skills/sdd-observability-invariants`), **Smoke Tests** (4–6 named end-to-end
scenarios), **Dependencies** (pinned package.json), **Project Layout**, **Open
Questions**.

### roadmap.md (sequencing — living document)

A flat list of numbered phases, each with: a one-sentence **goal** (the
engineering objective), a **"What this gives users/team/system"** line (the
plain-English benefit — mandatory, not optional, so a non-technical reader can
scan each phase's value), a checkbox task list, and a completion status. The goal
sentence is a contract: every noun in it is a deliverable, audited noun-by-noun
at done (Key Rule 11). Phases should be intentionally small — one focused session
each.

---

## Part 2: The Feature Spec

Each roadmap feature gets its own spec before implementation, in
`specs/YYYY-MM-DD-feature-name/` on its own git branch. Start with fresh agent
context. Ask the agent to interview you and produce three files. Every question
the agent asks carries its own recommendation and a one-line motivation (Key Rule
14). Ground every data-dependent decision in a real sample first (Key Rule 12).
Review all three before any coding. Commit the feature spec before implementation.

### requirements.md (what to build and why)

**Scope** (tables for fields/endpoints/states) + explicit **Out of Scope** list;
**Decisions** (explicit choices already made); **Success Criteria** (measurable);
**Observability Impact** (does this add an observable behavior/path/state/metered
call? how does it become visible? a blind spot is not "done"); **Failure Modes &
Unknowns** (for every signal, its `unknown`/`failed` representation — confirm it's
not a default that reads as a fact); **Analytics, Events & Usage** (which events
fire, when, with what properties; for metered external calls record real
inputs/usage/outcome as facts); **Context** (domain/tone, stack pointers,
cross-references).

### plan.md (how to build it — executed sequentially)

Numbered task groups, each themed. Standard groups: **Database, Components, Page
& Route, Navigation, Tests** (tests always last). Concrete steps referencing real
file paths; not so granular you specify variable names. **Instrumentation is part
of the task group that owns the behavior, not a bolt-on** — wiring observability
in last is how it gets dropped.

### validation.md (how to know it's done — executable)

**Grounding Evidence** (every data-dependent decision checked against a real
sample, cited); **Automated Tests** (top-level commands that must pass + specific
test-case checkboxes; **at least one test must exercise real collaborators —
don't mock both ends**); **Manual Checks** (specific human verifications);
**End-to-end on real data** (trigger the real behavior, inspect the real
artifact — green tests are necessary but not sufficient); **Analytics &
Observability Verification**; **Failure & Unknown Verification** (force each
failure path, confirm it records `unknown`/`failed`); **Quality/Tone Check**;
**Definition of Done** (one explicit sentence). validation.md mirrors plan.md
almost point for point — target 75%+ of checks tracing to plan/requirements.

**Definition of Done:** "All automated tests pass (including at least one that
doesn't mock both ends); every noun in the phase goal is delivered or explicitly
deferred with sign-off; the feature is proven end-to-end against the real running
system at least once and the evidence captured; all manual checks confirmed;
branch rebased cleanly onto main with no leftover TODOs."

---

## Part 3: The iterative process

**Starting a feature (checklist):** previous branch merged? context cleared?
next roadmap item still right? constitution up to date? real samples of every
external shape captured and cited? observability impact considered?

**During implementation:** one prompt to implement all task groups (or group by
group for large/sensitive areas, committing after each). Don't merge yet.

**Reviewing:** does it work as specified? did the agent drift? grounded in real
samples? does every noun in the goal appear? Tell the agent to fix things — don't
hand-edit (drift). 

**Validation:** run tests → typecheck → manual checks → **prove it once
end-to-end on real data** → read some tests under the debugger. Distinguish
"code-complete + unit-tested" from "verified working" — only the latter is the
goal.

**Replanning (own branch, after each merge):** constitution updates (new
decisions, new facts about external shapes), roadmap updates, process
improvements (is something repetitive → a skill?). Small changes in the replan
branch; large changes become new roadmap phases.

---

## Part 4: Advanced

**Skills** — reusable instruction packages invoked by name. Good candidates: the
feature-spec interview, changelog-on-merge, validation checklists, any repeated
multi-step process. Don't build skills too early — do the workflow manually 2–3
times first, build from real friction. **Backlog** — research mid-feature ideas,
write findings to a known location, schedule later with a link. **Agent
replaceability** — SDD is agent-agnostic: specs are plain markdown, skills follow
open standards; when you switch agents, your constitution and skills come with
you.

---

## Reference: Key Rules

See `skills/sdd-key-rules` for the full annotated list. In brief: (1) spec before
code; (2) changes through the agent; (3) fresh context per feature; (4) commit
spec before implementation; (5) small steps, frequent commits; (6) replan
between features; (7) surface open questions; (8) validation mirrors plan; (9)
the spec is living; (10) omissions aren't failures; (11) audit the goal
noun-by-noun at done; (12) ground data-dependent decisions in real samples; (13)
prove "done" on real data, not mocks; (14) interview with a recommendation, never
a neutral menu.
