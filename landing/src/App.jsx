import { useState } from "react";

const GH = "https://github.com/blutrich/sdd-kit";

function Copyable({ text, display }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
      className="codebox w-full text-left flex items-center justify-between gap-4 hover:translate-y-[-1px] transition-transform"
      title="Copy to clipboard"
    >
      <span>{display || text}</span>
      <span className="c shrink-0 text-xs">{copied ? "copied ✓" : "copy"}</span>
    </button>
  );
}

function SectionHead({ num, title, sub }) {
  return (
    <div className="mb-10">
      <div className="rule-strong mb-6" />
      <div className="flex flex-wrap items-baseline gap-x-6 gap-y-2">
        <span className="clause-num">ARTICLE {num}</span>
        <h2 className="display text-3xl md:text-4xl">{title}</h2>
      </div>
      {sub && <p className="mt-3 max-w-2xl text-[1.05rem] leading-relaxed text-[color:var(--ink-soft)]">{sub}</p>}
    </div>
  );
}

const CYCLE = [
  {
    n: "0",
    name: "Constitution",
    cmd: "/sdd-constitution",
    files: "domain-spec.md · engineering-spec.md · roadmap.md",
    desc: "The project agreement, written once through a grounded interview. What's true in any stack goes in the domain spec; what's specific to yours goes in the engineering spec.",
  },
  {
    n: "1",
    name: "Plan",
    cmd: "/sdd-plan",
    files: "requirements.md · plan.md · validation.md",
    desc: "One roadmap phase becomes a feature spec — scope, task groups, and an executable Definition of Done — before any code. A fresh-eyes gap reviewer checks it without seeing the planner's reasoning.",
  },
  {
    n: "2",
    name: "Implement",
    cmd: "/sdd-implement",
    files: "code + tests, on a branch",
    desc: "The implementer executes plan.md task group by task group with tests, keeping the spec in sync. It never merges.",
  },
  {
    n: "3",
    name: "Validate",
    cmd: "/sdd-validate",
    files: "real-data Definition of Done",
    desc: "validation.md runs as an executable checklist — including at least one end-to-end check on real data, and every failure/unknown path. Then the guardian, a separate adversarial agent, re-checks every gate and returns GO or NO-GO.",
  },
  {
    n: "4",
    name: "Replan",
    cmd: "/sdd-replan",
    files: "constitution · roadmap · skills, updated",
    desc: "After the merge, new decisions and newly-learned facts about external shapes fold back into the constitution. The system compounds instead of drifting.",
  },
];

const GATES = [
  {
    rule: "KR 1",
    name: "No spec → no code",
    refuses: "Asked to implement without a reviewed, committed feature spec.",
  },
  {
    rule: "KR 12",
    name: "Grounding",
    refuses: "A data-dependent decision isn't backed by a cited real sample — a real file, API response, log line, or DB row.",
  },
  {
    rule: "KR 13",
    name: "Real-data done",
    refuses: "“Done” is claimed on green tests that mock both ends.",
  },
  {
    rule: "KR 11",
    name: "Noun-by-noun",
    refuses: "A noun in the phase goal was silently dropped from the delivery.",
  },
];

const AGENTS = [
  ["constitution-author", "opus", "Writes the three Constitution files through a grounded interview."],
  ["feature-planner", "opus", "Produces the feature spec — grounding, interview, and spec design need judgment."],
  ["plan-gap-reviewer", "opus", "Fresh-eyes review of the spec before code. Never sees the planner's rationale — anti-anchoring."],
  ["implementer", "sonnet", "Executes an already-reviewed, grounded plan with tests. Speed in the loop; never merges."],
  ["reviewer", "opus", "Independent architect-level review for drift and ungrounded decisions."],
  ["validator", "opus", "Runs validation.md and forces every failure and unknown path."],
  ["sdd-guardian", "opus", "The final adversarial GO / NO-GO gate. Deliberately a different agent from the validator — never self-review."],
  ["replanner", "opus", "Folds learnings back into the constitution between features."],
];

const RULES = [
  "Write the spec before touching code.",
  "All changes through the agent — hand-edits cause drift.",
  "Fresh context per feature.",
  "Commit the spec before implementation.",
  "Small steps, frequent commits.",
  "Replan between every feature.",
  "Surface open questions explicitly.",
  "validation.md mirrors plan.md.",
  "The spec is living.",
  "Omissions aren't failures.",
  "Audit the goal noun-by-noun before claiming done.",
  "Ground data-dependent decisions in real samples.",
  "Prove “done” on real data, not mocks.",
  "Interview with a recommendation, never a neutral menu.",
  "Declare service contracts before coding — Services I depend on / Services I modify, cross-referenced.",
  "Verify caller wiring on every signature change — a green compile verifies types, not runtime wiring.",
];

export default function App() {
  return (
    <div className="relative">
      {/* top bar */}
      <header className="sticky top-0 z-40 border-b border-[color:var(--ink-faint)] bg-[color:var(--paper)]/90 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
          <a href="#" className="font-mono text-sm font-semibold tracking-wide">
            📜 sdd-kit
          </a>
          <nav className="hidden gap-6 font-mono text-[0.72rem] uppercase tracking-[0.18em] text-[color:var(--ink-soft)] md:flex">
            <a href="#cycle" className="hover:text-[color:var(--ink)]">Cycle</a>
            <a href="#gates" className="hover:text-[color:var(--ink)]">Gates</a>
            <a href="#commands" className="hover:text-[color:var(--ink)]">Commands</a>
            <a href="#agents" className="hover:text-[color:var(--ink)]">Agents</a>
            <a href="#rules" className="hover:text-[color:var(--ink)]">Rules</a>
            <a href="#ledger" className="hover:text-[color:var(--ink)]">Trade-offs</a>
            <a href="#install" className="hover:text-[color:var(--ink)]">Install</a>
          </nav>
          <a
            href={GH}
            target="_blank"
            rel="noreferrer"
            className="font-mono text-[0.72rem] uppercase tracking-[0.18em] underline underline-offset-4 hover:text-[color:var(--stamp-red)]"
          >
            GitHub ↗
          </a>
        </div>
      </header>

      {/* hero */}
      <section className="mx-auto max-w-5xl px-6 pt-20 pb-16 md:pt-28">
        <p className="kicker rise">A Spec-Driven Development harness for Claude Code and Codex</p>
        <h1 className="display rise mt-6 text-5xl md:text-7xl" style={{ animationDelay: "0.08s" }}>
          The spec is the brain.
          <br />
          The agent is the muscle.
        </h1>
        <div className="mt-8 flex flex-wrap items-start gap-x-10 gap-y-6">
          <p
            className="rise max-w-xl text-lg leading-relaxed text-[color:var(--ink-soft)]"
            style={{ animationDelay: "0.16s" }}
          >
            Write structured markdown specs <em>before</em> the agent writes a line of code. Your
            job shifts from typing code to writing clear specifications and reviewing output as an
            architect. And when a gate isn't met, the kit doesn't advise — it refuses.
          </p>
          <span className="stamp stamp-red stamp-in text-xl md:text-2xl">Fail-closed</span>
        </div>
        <div className="rise mt-10 max-w-xl space-y-3" style={{ animationDelay: "0.24s" }}>
          <Copyable text="/plugin marketplace add blutrich/sdd-kit" />
          <Copyable text="/plugin install sdd-kit@sdd-kit" />
        </div>
        <p className="mt-4 font-mono text-xs text-[color:var(--ink-soft)]">
          Repo-agnostic · harness-agnostic (Claude Code + Codex) · plain markdown + Python stdlib · MIT
        </p>
      </section>

      {/* creed */}
      <section className="mx-auto max-w-5xl px-6 pb-20">
        <div className="grid gap-8 md:grid-cols-3">
          {[
            [
              "Leverage",
              "Small spec changes produce large code changes. One sentence can move hundreds of lines — specs are higher-leverage than code.",
            ],
            [
              "Memory",
              "Agents are stateless; specs persist. The constitution survives across sessions, agents, and teammates — context decay solved on paper.",
            ],
            [
              "Truth",
              "A grounded spec beats a plausible one. The code tells you what it intends; only the data tells you what is true.",
            ],
          ].map(([t, d], i) => (
            <div key={t} className="rule pt-5">
              <div className="clause-num mb-2">§ 0.{i + 1}</div>
              <h3 className="display text-xl">{t}</h3>
              <p className="mt-2 leading-relaxed text-[color:var(--ink-soft)]">{d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* cycle */}
      <section id="cycle" className="mx-auto max-w-5xl scroll-mt-20 px-6 pb-20">
        <SectionHead
          num="I"
          title="The cycle"
          sub="The Constitution is written once and updated during Replan. Each feature runs Plan → Implement → Validate; between every feature, you Replan before starting the next."
        />
        <ol className="space-y-0">
          {CYCLE.map((s, i) => (
            <li key={s.n} className="rule grid gap-3 py-6 md:grid-cols-[64px_200px_1fr]">
              <div className="display text-4xl text-[color:var(--ink-faint)]" style={{ color: "rgba(29,26,20,0.22)" }}>
                {s.n}
              </div>
              <div>
                <h3 className="display text-xl">{s.name}</h3>
                <div className="mt-1 font-mono text-xs text-[color:var(--stamp-red)]">{s.cmd}</div>
                <div className="mt-1 font-mono text-[0.68rem] leading-relaxed text-[color:var(--ink-soft)]">
                  {s.files}
                </div>
              </div>
              <p className="leading-relaxed text-[color:var(--ink-soft)]">{s.desc}</p>
            </li>
          ))}
        </ol>
        <p className="mt-6 font-mono text-xs text-[color:var(--ink-soft)]">
          Live specs go in your project's <span className="text-[color:var(--ink)]">specs/</span> directory —
          the constitution at the root, each feature under{" "}
          <span className="text-[color:var(--ink)]">specs/YYYY-MM-DD-feature-name/</span>.
        </p>
      </section>

      {/* gates */}
      <section id="gates" className="mx-auto max-w-5xl scroll-mt-20 px-6 pb-20">
        <SectionHead
          num="II"
          title="The four gates"
          sub="The whole point. A router skill orients on your specs/ directory, routes intent — and refuses to proceed when a gate fails. Deterministic hooks back it up: once a Constitution exists, editing implementation code with no feature spec is blocked, not discouraged."
        />
        <div className="grid gap-6 md:grid-cols-2">
          {GATES.map((g) => (
            <div key={g.rule} className="border border-[color:var(--ink-faint)] bg-[color:var(--paper-deep)] p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="clause-num mb-1">{g.rule}</div>
                  <h3 className="display text-xl">{g.name}</h3>
                </div>
                <span className="stamp stamp-red text-[0.6rem]">Refused</span>
              </div>
              <p className="mt-3 leading-relaxed text-[color:var(--ink-soft)]">
                <span className="font-mono text-xs uppercase tracking-wider">Refuses when:</span>{" "}
                {g.refuses}
              </p>
            </div>
          ))}
        </div>
        <div className="mt-8 codebox">
          <div><span className="c"># the guardian's verdict is binary — and it shows its evidence</span></div>
          <div><span className="g">GO</span> — real-data DoD met · ≥1 test not mocking both ends · every goal noun delivered</div>
          <div><span className="r">NO-GO</span> — each failed gate reported with evidence. Never softened.</div>
        </div>
      </section>

      {/* commands */}
      <section id="commands" className="mx-auto max-w-5xl scroll-mt-20 px-6 pb-20">
        <SectionHead
          num="III"
          title="Commands"
          sub="Five commands are the lifecycle. Or just describe what you want — the sdd-router skill reads specs/ and routes for you."
        />
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="rule-strong font-mono text-[0.68rem] uppercase tracking-[0.16em] text-[color:var(--ink-soft)]">
                <th className="py-3 pr-4">You want to…</th>
                <th className="py-3 pr-4">Run</th>
                <th className="py-3">Produces</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["Start or refresh the project agreement", "/sdd-constitution", "specs/{domain-spec,engineering-spec,roadmap}.md"],
                ["Spec the next roadmap feature", "/sdd-plan", "specs/<date>-<feature>/{requirements,plan,validation}.md"],
                ["Build an approved feature", "/sdd-implement", "code + tests on a branch (no merge)"],
                ["Prove it's done", "/sdd-validate", "real-data DoD verdict + guardian GO / NO-GO"],
                ["Close the loop", "/sdd-replan", "updated constitution · roadmap · skills"],
                ["Check the kit is installed & enforcing", "/sdd-doctor", "health report: hooks · cache · branch↔spec contract"],
              ].map(([want, cmd, out]) => (
                <tr key={cmd} className="rule align-top">
                  <td className="py-4 pr-4 leading-snug">{want}</td>
                  <td className="py-4 pr-4 font-mono text-sm text-[color:var(--stamp-red)] whitespace-nowrap">{cmd}</td>
                  <td className="py-4 font-mono text-xs leading-relaxed text-[color:var(--ink-soft)]">{out}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-4 font-mono text-xs text-[color:var(--ink-soft)]">
          Installed as a plugin, commands namespace as /sdd-kit:sdd-plan and friends.
        </p>
      </section>

      {/* agents */}
      <section id="agents" className="mx-auto max-w-5xl scroll-mt-20 px-6 pb-20">
        <SectionHead
          num="IV"
          title="The agent team"
          sub="Best model per task: every judgment role runs on Opus; only the implementer runs on Sonnet. The guardian is deliberately a separate agent from the validator, so the final sign-off is never the checker grading its own work."
        />
        <div className="grid gap-x-10 gap-y-6 md:grid-cols-2">
          {AGENTS.map(([name, model, desc]) => (
            <div key={name} className="rule pt-4">
              <div className="flex items-baseline justify-between gap-4">
                <span className="font-mono text-sm font-semibold">{name}</span>
                <span
                  className={`font-mono text-[0.62rem] uppercase tracking-[0.16em] ${
                    model === "opus" ? "text-[color:var(--gold)]" : "text-[color:var(--stamp-green)]"
                  }`}
                >
                  {model}
                </span>
              </div>
              <p className="mt-1 text-[0.95rem] leading-relaxed text-[color:var(--ink-soft)]">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* rules */}
      <section id="rules" className="mx-auto max-w-5xl scroll-mt-20 px-6 pb-20">
        <SectionHead
          num="V"
          title="The 16 Key Rules"
          sub="The non-negotiables. Rules 12 and 13 were promoted to hard rules in v4 after a real build repeatedly shipped confidently-wrong code — decisions written from a plausible model of an external system, and done claimed on tests that mocked both ends. Rules 15 and 16 were added in v5 after the complementary failure: a unit-green change that silently broke the wire contract between components."
        />
        <ol className="grid gap-x-12 gap-y-3 md:grid-cols-2">
          {RULES.map((r, i) => (
            <li key={i} className="flex gap-4">
              <span className="clause-num mt-1 w-7 shrink-0 text-right">{i + 1}</span>
              <span className={i === 11 || i === 12 ? "font-semibold" : "text-[color:var(--ink-soft)]"}>
                {r}
                {(i === 11 || i === 12) && (
                  <span className="stamp stamp-green ml-3 align-middle text-[0.55rem]">hard rule</span>
                )}
              </span>
            </li>
          ))}
        </ol>
      </section>

      {/* honest ledger — pros & cons */}
      <section id="ledger" className="mx-auto max-w-5xl scroll-mt-20 px-6 pb-20">
        <SectionHead
          num="VI"
          title="The honest ledger"
          sub="Three months of dogfooding across a dozen real projects, ~140 feature specs. What the discipline gives, what it costs — and the one question that stays open."
        />
        <div className="grid gap-6 md:grid-cols-2">
          <div className="border border-[color:var(--ink-faint)] bg-[color:var(--paper-deep)] p-6">
            <span className="stamp stamp-green mb-4 text-[0.65rem]">Bless</span>
            <ul className="mt-4 space-y-4 leading-relaxed text-[color:var(--ink-soft)]">
              <li>
                <strong className="text-[color:var(--ink)]">Continuity.</strong> Agents are
                stateless; specs persist. A fresh session starts already grounded — the
                constitution and the next roadmap phase are injected at session start. Across
                sessions, agents, and teammates, nothing has to be re-explained.
              </li>
              <li>
                <strong className="text-[color:var(--ink)]">Bugs caught before merge.</strong>{" "}
                Guardian NO-GOs stopped a live-deploy overclaim, a guard unreachable under live
                input, and a bypassable phone-guard. Grounding caught a false RED; real-data
                validation refuted 2 of 5 claimed P0s. "NO-GO gates are cheaper than prod bugs."
              </li>
              <li>
                <strong className="text-[color:var(--ink)]">Leverage and auditability.</strong> One
                spec sentence moves hundreds of lines of code — and every decision has a written,
                grounded reason someone can check a month later.
              </li>
            </ul>
          </div>
          <div className="border border-[color:var(--ink-faint)] bg-[color:var(--paper-deep)] p-6">
            <span className="stamp stamp-red mb-4 text-[0.65rem]">Curse</span>
            <ul className="mt-4 space-y-4 leading-relaxed text-[color:var(--ink-soft)]">
              <li>
                <strong className="text-[color:var(--ink)]">Ceremony costs real time.</strong>{" "}
                Spec-writing is unglamorous work that's easy to leave unbilled, and small changes
                tempt shortcuts — in practice, several projects invented an unofficial one-file
                spec rather than run the full triple.
              </li>
              <li>
                <strong className="text-[color:var(--ink)]">Discipline decays.</strong> Checklists
                get written and boxes don't get ticked (one repo: 0 of 759). Gates only bite while
                enforcement holds — and people route around gates that get in the way.
              </li>
              <li>
                <strong className="text-[color:var(--ink)]">The skeptic has a point.</strong>{" "}
                <em>"It feels a little too cutesy and a little too rigid. It is just a plan. It is
                just a text file."</em> Worth keeping on the wall — process that stops earning its
                keep is just process.
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-6 border-2 border-[color:var(--ink)] p-6">
          <div className="flex flex-wrap items-baseline justify-between gap-3">
            <h3 className="display text-xl">Open verdict: the weight of the docs</h3>
            <span className="font-mono text-[0.62rem] uppercase tracking-[0.18em] text-[color:var(--gold)]">
              bless & curse
            </span>
          </div>
          <p className="mt-3 leading-relaxed text-[color:var(--ink-soft)]">
            Specs accumulate. Long-lived repos have crossed <strong>200% of a context window</strong>{" "}
            in spec text alone. As <em>institutional memory</em>, that weight is the blessing — any
            agent, any day, can reconstruct why every decision was made. As <em>live context</em>,
            it's the curse — bloat, drift, compaction pressure. The deciding variable is replan
            discipline: archive finished feature dirs, keep the roadmap as the index rather than
            the corpus. Dead weight is what specs become when the loop stops closing.
          </p>
        </div>
      </section>

      {/* install */}
      <section id="install" className="mx-auto max-w-5xl scroll-mt-20 px-6 pb-20">
        <SectionHead
          num="VII"
          title="Install & first run"
          sub="One kit, two harnesses. A standard Claude Code plugin, or a Codex skills + hooks layout the installer writes for you. Five minutes to your first gated feature."
        />
        <div className="grid gap-10 md:grid-cols-3">
          <div>
            <h3 className="display text-xl">A · Claude Code · marketplace</h3>
            <div className="mt-4 space-y-3">
              <Copyable
                text="claude plugin marketplace add blutrich/sdd-kit && claude plugin install sdd-kit@sdd-kit"
                display="claude plugin marketplace add blutrich/sdd-kit && claude plugin install …"
              />
            </div>
            <p className="mt-3 leading-relaxed text-[color:var(--ink-soft)]">
              Commands appear as <span className="font-mono text-sm">/sdd-kit:sdd-plan</span>, skills
              auto-trigger, agents join the team.
            </p>
          </div>
          <div>
            <h3 className="display text-xl">B · Claude Code · vendor it</h3>
            <div className="mt-4">
              <Copyable
                text="git clone https://github.com/blutrich/sdd-kit .claude/skills/sdd-kit"
                display="git clone …/sdd-kit .claude/skills/sdd-kit"
              />
            </div>
            <p className="mt-3 leading-relaxed text-[color:var(--ink-soft)]">
              Copied into your repo, Claude Code auto-loads it as a project-scoped plugin for
              everyone who clones — hooks included. No install step.
            </p>
          </div>
          <div>
            <h3 className="display text-xl">C · Codex · installer</h3>
            <div className="mt-4 space-y-3">
              <Copyable
                text="git clone https://github.com/blutrich/sdd-kit ~/sdd-kit && python3 ~/sdd-kit/scripts/sdd_install.py --harness codex"
                display="python3 ~/sdd-kit/scripts/sdd_install.py --harness codex"
              />
            </div>
            <p className="mt-3 leading-relaxed text-[color:var(--ink-soft)]">
              Writes <span className="font-mono text-sm">.agents/skills/</span> (so{" "}
              <span className="font-mono text-sm">$sdd-plan</span> is{" "}
              <span className="font-mono text-sm">/sdd-plan</span>),{" "}
              <span className="font-mono text-sm">.codex/hooks.json</span> with the same three
              guard scripts, and an AGENTS.md block. Same gates, same specs — switch tools
              mid-project and nothing moves.
            </p>
          </div>
        </div>

        <div className="mt-12">
          <h3 className="display mb-4 text-xl">Then, in your project:</h3>
          <div className="codebox">
            <div><span className="c"># 1 · write the project agreement (once)</span></div>
            <div>/sdd-kit:sdd-constitution</div>
            <div>&nbsp;</div>
            <div><span className="c"># 2 · spec the first feature — interview, grounding, fresh-eyes review</span></div>
            <div>/sdd-kit:sdd-plan</div>
            <div>&nbsp;</div>
            <div><span className="c"># 3 · build it, task group by task group, on a branch</span></div>
            <div>/sdd-kit:sdd-implement</div>
            <div>&nbsp;</div>
            <div><span className="c"># 4 · prove it on real data · guardian says </span><span className="g">GO</span><span className="c"> or </span><span className="r">NO-GO</span></div>
            <div>/sdd-kit:sdd-validate</div>
            <div>&nbsp;</div>
            <div><span className="c"># 5 · merge, then fold the learnings back</span></div>
            <div>/sdd-kit:sdd-replan</div>
          </div>
          <p className="mt-4 leading-relaxed text-[color:var(--ink-soft)]">
            Enforcement is on by default: once a Constitution exists, the{" "}
            <span className="font-mono text-sm">spec-before-code</span> hook blocks edits to
            implementation code on a branch with no feature spec. Downgrade per shell with{" "}
            <span className="font-mono text-sm">SDD_GUARD=warn</span> or{" "}
            <span className="font-mono text-sm">SDD_GUARD=off</span>. It never touches specs, docs,
            config, or tests.
          </p>
          <p className="mt-4 leading-relaxed text-[color:var(--ink-soft)]">
            And since v0.3.0 the router runs the whole cycle{" "}
            <em>autonomously by default</em> — plan → implement → validate → guardian, chained
            without approval round-trips, auto-remediating mechanical gate failures. It stops for
            you only at a <strong>one-way door</strong>: merge, deploy, destructive ops, external
            side effects, or dropping a goal noun. Every cycle ends with a plain-prose operator
            summary before the merge question.
          </p>
        </div>
      </section>

      {/* footer */}
      <footer className="border-t-2 border-[color:var(--ink)]">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-6 px-6 py-10">
          <div>
            <div className="display text-lg">📜 sdd-kit</div>
            <p className="mt-1 max-w-md font-mono text-xs leading-relaxed text-[color:var(--ink-soft)]">
              Methodology: Spec-Driven Development v4. Harness shape inspired by cc10x (Rom Iluz).
              Assembled for Ofer Blutrich &amp; Tsahi (Isaac Zeevi). MIT license.
            </p>
          </div>
          <div className="flex items-center gap-6">
            <a
              href={GH}
              target="_blank"
              rel="noreferrer"
              className="font-mono text-xs uppercase tracking-[0.18em] underline underline-offset-4 hover:text-[color:var(--stamp-red)]"
            >
              github.com/blutrich/sdd-kit
            </a>
            <span className="stamp stamp-green text-[0.6rem]">GO</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
