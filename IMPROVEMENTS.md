# sdd-kit — Improvement Proposals (2026-08-11)

A replan on the kit itself. Every item below is grounded in real usage evidence
gathered from: the kit's own repo + git history, **12 SDD projects on this
machine** (~140 feature specs, 300+ committed grounding samples), Obsidian
project memories and daily notes (May–Aug 2026), and the e2e dogfood record.

The kit's own discipline applied to itself: no proposal here is speculative —
each cites where the friction actually happened.

> **Status (2026-08-11, same day):** Section A is **implemented** — A1 branch
> resolver (exact → last-segment → slug), A2 Bash-write advisory hook
> (`scripts/bash_write_guard.py`), A3 main/detached-HEAD messages, A4
> dir-aware + anchored test exemption, A5 committed-not-just-exists check,
> A6 widened CODE_EXTS, A7 `scripts/check_grounding.py` wired into
> `/sdd-validate`, A8 `/sdd-doctor` (+ it immediately caught this machine's
> stale 0.2.0 plugin cache), A9 docstring fixed. Also landed: **B1** gate
> graph rewired (noun_by_noun attached, implement entry gates completed,
> all_gates_pass includes plan_reviewed, guardian un-conflated + verdict
> extended to 7 gates), **B4 partially** (homepage/repository in plugin.json,
> workflow.json name unified, bogus $schema dropped), and a phase-aware
> roadmap scanner in the SessionStart hook. All covered by a new real-git-repo
> test suite: `tests/test_hooks.py`, 24 tests green. A skills audit pass then
> fixed the **skills layer**: sdd-key-rules description un-staled (14→16) and
> the broken 15/16 list structure repaired; the grounding skill's "or its
> structure" loophole closed (+ check_grounding.py cited); the router got a
> kit-root resolution note (**B3 for skills** — agents/commands still have bare
> paths) and an /sdd-doctor pointer. Still open: B2, B3 (agents/commands), B5, C, D.
>
> **Status 2026-08-29 (v0.5.0):** harness-agnostic. Codex now shares the hook
> contract, so the same three scripts run under both; `scripts/sdd_harness.py`
> owns every harness-specific name, the guard reads `apply_patch` headers,
> `sdd_install.py` writes the Codex layout (`.agents/skills`, `.codex/hooks.json`,
> `AGENTS.md`), and the doctor checks whichever layout it's running in.
> Fixed on the way: a macOS `/var`→`/private/var` relpath bug that let exempt
> prefixes be dodged.

---

## A · Fix the enforcement layer (P0 — bugs that already bit)

### A1. Fix the branch-name → spec-dir resolution bug
**Evidence:** Marketing suite `specs/roadmap.md:568` records it as a *"STANDING
external-tooling liability… has now recurred 4 times."* Also hit
climbingbrowser. The guard resolves `specs/<branch>/requirements.md` literally,
so a branch named `spec/2026-07-19-word-rules` looks for
`specs/spec/2026-07-19-word-rules/requirements.md` — a path nothing creates.
**Fix:** resolve the spec dir by matching the *last path segment* of the branch
name against `specs/*/` dirs (and/or slugify `/` → `-`). Add a repo-local
override (`.sdd/branch-spec-map` or git config `sdd.specDir`) as an escape
hatch. Kill the documented workaround ("create a throwaway pointer file at
`specs/spec/<branch>/…` then delete it") by making it unnecessary.

### A2. Close the Bash bypass — it's now a *documented convention* in a dogfood repo
**Evidence:** marketing suite `2026-07-19-word-rules/validation-runs.md:177`:
source files were written via **Bash heredoc** specifically to dodge the
`Edit|Write|MultiEdit` matcher, and the repo's CLAUDE.md was amended to
legitimize the bypass. The kit's single deterministic gate was routed around,
permanently. **Fix:** (a) fix A1 so nobody *needs* the bypass; (b) add a
`PreToolUse` Bash matcher that flags heredoc/`>` redirects targeting code
extensions (advisory is enough — visibility kills the quiet workaround); (c) a
`Stop`-hook audit comparing files changed this session against spec presence.

### A3. Give `main` a documented story instead of a silent lockout
Working on `main`/`master` in a Constitution-bearing repo blocks *every* code
edit — `specs/main/requirements.md` never exists. No hotfix path, no message
explaining it. **Fix:** detect default branch and emit a specific message
("you're on main — create a feature branch or set SDD_GUARD=warn for a
hotfix"), and document the branch↔spec-dir contract prominently (it is the #1
new-user trip wire; today it's one passing mention in `commands/sdd-plan.md`).

### A4. Fix the test-file exemption (both directions)
`"test" in basename` exempts `latest.ts`, `contest.py`, `protest.js`; while
`tests/helpers.py` and `__tests__/setup.js` are **not** exempt — contradicting
the README's "tests always pass through." **Fix:** dir-aware check
(`tests/`, `__tests__/`, `spec/` path segments) + anchored basename patterns
(`test_*`, `*_test.*`, `*.test.*`, `*.spec.*`).

### A5. Check *committed*, not *exists*
`spec_before_code` and `spec_committed` both assert the spec is **committed**;
the hook only does `os.path.isfile` on one of the three files. A five-line
`git ls-files` check closes the gap the guardian is later asked to catch by
reading git history manually.

### A6. Widen (or invert) CODE_EXTS
`.sh`, `.sql`, `.vue`, `.svelte`, `.ex`, `.dart`, `.scala`, `.tf` get zero
enforcement in a kit whose first line says "repo-agnostic" — and every
`.json/.yaml/.toml` is exempt, so CI config, IaC, and migration YAML are
spec-free. Consider inverting to an exempt-list-only model.

### A7. Mechanically enforce the "most-faked gate"
`sdd-guardian.md` itself calls `spec_grounded` the *"most-faked gate."* The fix
is trivially scriptable: check `specs/<feature>/samples/` is non-empty and each
sample opens with a provenance line (regex). Wire it into `/sdd-validate` (and
optionally the guard hook). Today, only 14/50 physio-ai requirements files have
a Grounding Samples section at all.

### A8. Add `/sdd-doctor`
Nothing verifies the hooks actually loaded. If `python3` is missing (Windows),
the plugin root doesn't resolve, or the installed version is stale, the user
gets a kit that *appears* installed and enforces nothing. A doctor command
checks: python version (≥3.10 note), hooks firing, plugin version vs remote,
specs dir resolution, branch contract, and gate wiring. **This machine is the
proof:** the user-scope plugin cache is at **0.2.0** while the repo is at
0.3.0+.

### A9. Fix the guard script's self-description
Docstring says *"By default this is ADVISORY"*; the code defaults to
`SDD_GUARD=block`. Two contradicting descriptions in one 121-line file. Also
drop the dead `import re`.

---

## B · Repair internal drift (P1 — the kit disagrees with itself)

### B1. Rewire the gate graph in `config/workflow.json`
- `noun_by_noun` is defined but attached to **no phase** — add to `validate.exit_gates`.
- `implement.entry_gates` omits `spec_committed` and `plan_reviewed` — an
  unreviewed, uncommitted spec satisfies IMPLEMENT's declared entry today.
- `all_gates_pass` omits `plan_reviewed` — the guardian never verifies the
  plan-gap-reviewer ran, the most expensive-to-skip gate in the design.
- `guardian.next: "merge"` dangles — no `merge` phase object exists.
- `sdd-guardian.md` gate #1 is labeled `spec_before_code` (KR1) but its
  instruction is the `spec_committed` (KR4) check — un-conflate.

### B2. Un-fork the playbook and the Key Rules numbering
The kit ships `sdd-playbook-v4.md` and declares it the tiebreaker ("when they
and this disagree, this wins") — yet it's the **only file never updated**, so
the stated precedence rule makes the stalest document authoritative. Meanwhile
**playbook v5 (42KB, Jul 17) exists only inside physio-ai** and was never
folded back. Worse, the numbering has forked: the kit's new **KR 15/16** are
the integration-contract guard, while physio-ai's v6 uses **15/16/17** for
Continuity Handoff / Regression Gate / Reusable Asset Registry.
**Fix:** import physio-ai's v5/v6 material, renumber its three rules as
**KR 17/18/19**, publish `sdd-playbook-v5.md` in `reference/`, and either keep
the playbook current or demote the tiebreaker clause to point at
`config/workflow.json`.

### B3. Fix plugin-internal path resolution
Agents/commands/skills reference `reference/sdd-playbook-v4.md`,
`config/workflow.json`, and `templates/*.template.md` by **bare relative
path**. Under a marketplace install, cwd is the user's project — every one of
those reads fails; only `hooks.json` uses `${CLAUDE_PLUGIN_ROOT}`. The guardian
literally cannot read the gate registry it's told to enforce.

### B4. Manifest hygiene
`workflow.json` says `"name": "sdd"`, plugin.json says `"sdd-kit"`; plugin.json
has no `homepage`/`repository` (the real repo appears nowhere in any manifest);
marketplace.json entry has no version; no CHANGELOG despite three version
bumps. Add all four; drop the meaningless `$schema` key in workflow.json.

### B5. Complete the routing table
`reference/where-does-it-go.md` has no row for `specs/<feature>/samples/` (the
artifact the hardened grounding gate *requires*) nor for validation run logs
(see C1).

---

## C · Fold field-proven inventions back into the kit (P1 — users already built these)

### C1. Validation run log — fix checkbox rot
**Evidence:** checklists are written but almost never ticked — pr-agent
**0/759** boxes checked, podlearn 2/297, marketing suite 3/223; only ClimbClaw
(219/318) ticks habitually. Meanwhile two projects independently invented the
missing artifact: `validation-runs.md` / `validation-results.md` — checklist as
*spec*, runs as *append-only dated log* (which is where the guardian NO-GO
stories actually live). **Fix:** add `validation-runs.template.md`, have
`validator` append a dated run entry each execution, and make the DoD reference
the latest run rather than checkbox state.

### C2. Official sub-constitution support
physio-ai invented **five nested constitutions** (`specs/{calendar,
observability, patient-portal, payments, webapp}/` each with its own
domain/engineering/roadmap) because one roadmap couldn't hold 65 features. The
kit has no concept of this — router and `inject_constitution.py` see only the
top level. Formalize: `specs/<area>/` sub-constitutions, router awareness,
hook awareness (report next phase *per area*).

### C3. Spec archiving — the context-bloat killer
**Evidence:** physio-ai's repo doc counter hit **330k tokens (165% of a context
window)**, later **424k / 212%**; daily notes track compaction pressure
worsening for weeks. Specs are append-only today. **Fix:** a replan step that
moves ✅-done feature dirs to `specs/archive/<year>/`, keeps a one-line-per-
feature `specs/INDEX.md`, and (optionally) compacts the roadmap. The
SessionStart hook should read the index, not the corpus.

### C4. An official "patch spec" tier (SDD-lite)
**Evidence:** four projects independently broke convention with a single ad-hoc
`spec.md` for small changes (physio-ai hotfixes, base44-marketing ×2, seo-agents),
and physio-ai parked `analysis.md` files in feature dirs. The demand is real;
today it's rule-breaking. **Fix:** define a sanctioned one-file
`patch.md` tier for small, low-risk changes — still requiring a grounding
citation + a real-data DoD line — with the guard accepting it
(`specs/<branch>/patch.md`). Bounded by explicit criteria (no schema change, no
new observable behavior, ≤N files).

### C5. Generalize the grounding-capture ritual into `/sdd-capture`
**Evidence:** physio-ai created `sdd-capture-ls-webhook` explicitly after
*"3x friction"* — the same manual capture done three times before automation.
A generic `/sdd-capture <cmd>` that runs the command, saves output under
`specs/<feature>/samples/` with the provenance header (command + date), and
prints the citation line would make KR12 nearly free — and A7 enforceable.

### C6. Stall detection in the SessionStart hook
**Evidence:** four Tier-2 projects wrote a constitution (+1 spec) and then
**stalled** — nta-portal, BackToLife, oferblutrich-site, and Marketing
Superagent (whose P1 has sat GO-gated but unbuilt since June, with the roadmap
checkbox still unchecked). The hook already reports the next phase; add *age*:
"P1 spec'd 52 days ago, plan-gap-reviewer GO, never implemented." Staleness
made visible is the cheapest nudge that exists.

### C7. De-web the plan template
`plan.template.md`'s fixed groups (Database / Components / Page & Route /
Navigation) are web-app-specific in a "repo-agnostic" kit. base44-marketing
formally opted out of parts of the structure; CLI/pipeline/library projects get
nonsense groups. Mark the groups illustrative and ship 2–3 variants (webapp /
CLI-service / library-pipeline). Keep "Tests always last."

### C8. Adopt the drift tripwire
Marketing suite built `scripts/check-spec-drift.sh` after its specs silently
fell behind the shipped console ("three gaps caught and recorded"). Port it
into the kit (`scripts/check_spec_drift.py`) and run it during `/sdd-replan`.

---

## D · Adoption, docs, self-application (P2)

### D1. Ship a worked example
Templates are all `<placeholder>`; a new user reads 250+ lines of README and
never sees a *finished* artifact. The Marketing Superagent
`2026-06-20-entities-foundation` spec is 100%-template-conformant with real
provenance-headed samples — anonymize and ship it as `examples/`.

### D2. Put the kit under its own discipline
The kit has zero tests for its two Python hooks and no `specs/` of its own — a
harness whose thesis is "prove it on real data" should dogfood itself. Give
sdd-kit a constitution + roadmap (A/B/C items above *are* the roadmap) and a
CI job running hook unit tests (the branch-name matrix from A1/A3/A4 is the
test list).

### D3. Autonomous mode deserves front-page documentation
v0.3.0 ships `automation.mode: "autonomous"` **on by default** — the router
auto-chains plan→implement→validate→guardian and stops only at one-way doors.
That's the kit's biggest behavioral change ever and the README explains it
nowhere (only the router skill does). Document it, with the
`human_stop_conditions` list, and consider opt-in for first install.

### D4. Housekeeping on this machine
- The user-scope installed plugin is **0.2.0** (cache, installed Jun 20) while
  origin/main is 0.3.0+ — run `/plugin update sdd-kit` (or reinstall).
- `/Users/blutrich/Documents/DEV/sdd-kit/sdd-kit/` is a second, now-stale
  checkout nested inside the repo (untracked). The root checkout has been
  fast-forwarded past it — the nested copy can be deleted.
- physio-ai vendors its own 0.3.0 copy in 12 worktrees — after B2 lands, one
  update pass brings them in line.
- Obsidian: **7 broken wikilinks** point to a nonexistent
  `Personal/Dev/SDD Kit/Project Memory` — the most-cited project in the vault
  has no page. Create it (this document is most of the content).

### D5. Unbilled process time
FREEDOM Tracker records SDD spec/gap-review hours as **NOT billed** on the NTA
Portal engagement. Not a kit bug — but if SDD is the differentiator (the ADLC
consulting lead maps SDD = Inception), the spec phase is billable architecture
work and should be scoped as such in future engagements.

---

## What already works — keep it

The evidence also shows the core design *earning its keep*, repeatedly:
guardian NO-GOs caught real failure modes pre-merge (ClimbClaw coach-phone-guard:
3 real gates; marketing suite: a live-deploy overclaim with an impossible
timestamp; podlearn: a NO-GO that correctly blocked task groups 4–6), the
grounding gate caught a **false RED** before it could mislead a renewal motion
(EnterpriseOS), real-data checks **refuted 2 of 5 claimed P0s** (podlearn
security), and KR12 *"falsified four handed-down premises before any code"*
(PhysioAI Lite). The fail-closed architecture is validated; these proposals are
about closing the gaps people actually routed around.
