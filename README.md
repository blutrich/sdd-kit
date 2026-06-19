# sdd-kit

**A repo-agnostic, agent-agnostic Spec-Driven Development harness for Claude Code.**

Write structured markdown **specs before the agent writes a line of code**. The
spec is the brain; the agent is the muscle. Your job shifts from typing code to
writing clear specifications and reviewing output as an architect. A *grounded*
spec beats a *plausible* one — every decision that depends on the real shape of
something external (a file format, an API response, a log line, the live DB) is
verified against the real artifact **before** it's written down. The code tells
you what it *intends*; only the data tells you what is *true*.

> Structure mimics [cc10x](https://github.com/romiluz13/cc10x): a **router** skill
> is the brain, **agents** are phase specialists, **commands** are the lifecycle,
> **templates** are the six spec files, **skills** carry the durable rules.
> Methodology is the [Spec-Driven Development v4 playbook](reference/sdd-playbook-v4.md).

---

## The SDD cycle

```mermaid
flowchart TD
    C["📜 CONSTITUTION<br/>specs/domain-spec.md · engineering-spec.md · roadmap.md<br/><i>written once, updated during Replan</i>"]
    C --> L

    subgraph L["🔁 FEATURE LOOP — per specs/YYYY-MM-DD-feature-name/"]
        direction LR
        P["1 · PLAN<br/>requirements.md<br/>plan.md · validation.md"]
        I["2 · IMPLEMENT<br/>code + tests<br/>on a branch"]
        V["3 · VALIDATE<br/>real-data<br/>Definition of Done"]
        P --> I --> V
    end

    V --> R["♻️ REPLAN<br/>fold new decisions + real-shape facts back into<br/>constitution · roadmap · process · skills"]
    R -->|next feature| L
```

The Constitution is written once at the start and updated during Replan. Each
feature gets its own spec (**Plan → Implement → Validate**). Between every
feature, you **Replan** before starting the next.

---

## How the router decides

Describe what you want, or run a command. The **`sdd-router`** skill orients on
your `specs/` directory, then routes — and **fails closed** on any gate.

```mermaid
flowchart TD
    START([Request or command]) --> ORIENT{"Read specs/ —<br/>does a Constitution exist?"}
    ORIENT -->|No| CONST["/sdd-constitution<br/>→ constitution-author"]
    ORIENT -->|Yes| INTENT{Intent?}

    INTENT -->|"plan / spec / what's next"| PLAN["/sdd-plan<br/>→ feature-planner"]
    INTENT -->|"implement / build"| GATE1{"Approved, committed<br/>feature spec exists?"}
    INTENT -->|"validate / is it done"| VAL["/sdd-validate<br/>→ validator + reviewer"]
    INTENT -->|"replan / just merged"| REPLAN["/sdd-replan<br/>→ replanner"]

    GATE1 -->|No| PLAN
    GATE1 -->|Yes| GATE2{"Every data-dependent<br/>decision grounded in<br/>a real sample?"}
    GATE2 -->|No| GROUND["⛔ Stop — capture the<br/>real sample first<br/>(Key Rule 12)"]
    GATE2 -->|Yes| IMPL["/sdd-implement<br/>→ implementer"]

    IMPL --> VAL
    VAL --> DONE{"Real-data DoD met?<br/>≥1 test not mocking both ends?<br/>every goal noun delivered?"}
    DONE -->|No| FIX["⛔ Report what failed<br/>with evidence — don't soften"]
    DONE -->|Yes| MERGE([Merge]) --> REPLAN
```

**The fail-closed gates** (the whole point):

| Gate | Rule | Refuses when |
|---|---|---|
| No spec → no code | KR 1 | asked to implement without a reviewed, committed feature spec |
| Grounding | KR 12 | a data-dependent decision isn't backed by a cited real sample |
| Real-data done | KR 13 | "done" is claimed on tests that mock both ends |
| Noun-by-noun | KR 11 | a noun in the phase goal was silently dropped |

---

## Where does a decision go?

```mermaid
flowchart TD
    Q{"Is this decision…"}
    Q -->|technology-INDEPENDENT<br/>true in any stack| D["domain-spec.md"]
    Q -->|technology-DEPENDENT<br/>specific to your stack| E["engineering-spec.md"]
    Q -->|sequencing<br/>what gets built when| RM["roadmap.md"]
    Q -->|per-feature scope / criteria| RQ["requirements.md"]
    Q -->|per-feature task list| PL["plan.md"]
    Q -->|per-feature done-proof| VL["validation.md"]
```

`"confidence ≥ 0.6 → confirmed"` is a **business rule** → domain-spec. The ORM
query that implements it is **technology-dependent** → engineering-spec. Full
table: [reference/where-does-it-go.md](reference/where-does-it-go.md).

---

## Commands

| You want to… | Run | Agent | Produces |
|---|---|---|---|
| Start/refresh the project agreement | `/sdd-constitution` | `constitution-author` | `specs/domain-spec.md`, `engineering-spec.md`, `roadmap.md` |
| Spec the next roadmap feature | `/sdd-plan` | `feature-planner` | `specs/<date>-<feature>/{requirements,plan,validation}.md` |
| Build an approved feature | `/sdd-implement` | `implementer` | code + tests on a branch (no merge) |
| Prove it's done | `/sdd-validate` | `validator` + `reviewer` | real-data Definition-of-Done verdict |
| Close the loop before the next feature | `/sdd-replan` | `replanner` | updated constitution/roadmap/skills |

When installed as a plugin, commands are namespaced: `/sdd-kit:sdd-plan`, etc.

---

## The 14 Key Rules (the non-negotiables)

Full annotated list: [skills/sdd-key-rules](skills/sdd-key-rules/SKILL.md).

1. Write the spec before touching code. **2.** All changes through the agent, never
hand-edits (manual edits cause drift). **3.** Fresh context per feature. **4.**
Commit the spec before implementation. **5.** Small steps, frequent commits. **6.**
Replan between every feature. **7.** Surface open questions explicitly. **8.**
validation.md mirrors plan.md. **9.** The spec is living. **10.** Omissions aren't
failures. **11.** Audit the goal **noun-by-noun** before claiming done. **12.**
**Ground data-dependent decisions in real samples.** **13.** **Prove "done" on real
data, not mocks.** **14.** Interview with a recommendation, never a neutral menu.

Rules **12** and **13** were promoted to hard rules in v4 after a real build
repeatedly shipped confidently-wrong code (decisions written from a *plausible*
model of an external system, and "done" claimed on green tests that mocked both
ends). They are the cheapest insurance against the most expensive class of bug.

---

## What's in the box

```
sdd-kit/
├── .claude-plugin/
│   └── plugin.json                 # plugin manifest (identity)
├── agents/                         # phase specialists
│   ├── constitution-author.md      #   writes the 3 Constitution files
│   ├── feature-planner.md          #   writes the 3 feature-spec files
│   ├── implementer.md              #   executes plan.md, no merge
│   ├── validator.md                #   runs validation.md, forces failure paths
│   ├── reviewer.md                 #   architect-level drift/grounding review
│   └── replanner.md                #   folds learnings back into the constitution
├── commands/                       # the lifecycle: /sdd-constitution … /sdd-replan
│   └── sdd-{constitution,plan,implement,validate,replan}.md
├── skills/                         # durable rules + the brain
│   ├── sdd-router/                 #   THE entry point — routes intent, fails closed
│   ├── sdd-key-rules/              #   the 14 invariants
│   ├── sdd-grounding-discipline/   #   Key Rule 12 — real samples before decisions
│   └── sdd-observability-invariants/ # the seam + "unknown is never success"
├── templates/                      # copy these, never start blank
│   └── {domain-spec,engineering-spec,roadmap,requirements,plan,validation}.template.md
└── reference/
    ├── sdd-playbook-v4.md           # the canonical methodology (source of truth)
    └── where-does-it-go.md          # content → file routing table
```

---

## Install

This is a standard Claude Code plugin. Two ways:

**1. Vendor it (simplest, shared per-repo).** Copy this folder into your project
(e.g. as `.agent/` or `.claude/sdd-kit/`) and point your agent at it. The *live*
specs you generate live in your project's `specs/` directory — nothing here is
tied to a specific repo, stack, or company.

**2. Marketplace install (reusable across all your projects).** Add the repo to a
Claude Code marketplace and install:

```bash
/plugin marketplace add <owner>/sdd-kit
/plugin install sdd-kit
```

Commands then appear as `/sdd-kit:sdd-plan` and friends; skills auto-trigger via
their descriptions; agents are available to the `Task` tool.

---

## Why it works

- **Small spec changes produce large code changes.** One sentence can move
  hundreds of lines — specs are higher-leverage than code.
- **Specs solve context decay.** Agents are stateless; specs persist across
  sessions, agents, and teammates.
- **Specs improve intent fidelity.** Every decision you don't write down, the
  agent makes on its own — and usually wrong.
- **Agent-agnostic.** Specs are plain markdown; skills follow open standards. Switch
  agents and your constitution + skills come with you.

---

## Credits

Methodology: Spec-Driven Development v4. Harness shape inspired by
[cc10x](https://github.com/romiluz13/cc10x) (Rom Iluz). Assembled for Ofer
Blutrich & Tsahi (Isaac Zeevi).
