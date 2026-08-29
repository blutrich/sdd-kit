#!/usr/bin/env python3
"""sdd-install — lay the kit out for a coding agent harness (Claude Code, Codex, or both).

sdd-kit is one set of files — router skill, rules skills, lifecycle commands,
agent roles, templates, hook scripts — that different harnesses discover in
different places:

                    Claude Code                      Codex
  skills            .claude/skills/<kit>/skills/     .agents/skills/<name>/SKILL.md
  commands          .claude/skills/<kit>/commands/   .agents/skills/<cmd>/SKILL.md (shim, invoked as $sdd-plan)
  hooks             <kit>/hooks/hooks.json (auto)    .codex/hooks.json (same schema)
  session context   SessionStart hook                SessionStart hook + AGENTS.md block

This script writes those layouts. Stdlib only, idempotent, safe to re-run
after every kit upgrade. Never touches implementation code.

Usage:
  python3 scripts/sdd_install.py [--harness claude|codex|both] [--scope project|user]
                                 [--project DIR] [--link] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT_PARTS = ("skills", "commands", "agents", "templates", "reference", "config",
             "scripts", "hooks", ".claude-plugin", "README.md", "LICENSE")
HOOK_SCRIPTS = {
    "SessionStart": [(None, "inject_constitution.py")],
    "PreToolUse": [("Edit|Write|MultiEdit|apply_patch", "spec_before_code_guard.py"),
                   ("Bash", "bash_write_guard.py")],
}
AGENTS_START, AGENTS_END = "<!-- sdd-kit:start -->", "<!-- sdd-kit:end -->"


def log(msg, dry):
    print(("[dry-run] " if dry else "") + msg)


def frontmatter_description(path: str) -> str:
    text = open(path, encoding="utf-8").read()
    m = re.search(r"^description:\s*(.+?)\s*$", text, re.MULTILINE)
    return m.group(1).strip().strip('"') if m else ""


def copy_kit(dest: str, link: bool, dry: bool):
    """Put the whole kit at dest (copy or symlink)."""
    if os.path.islink(dest) or os.path.isfile(dest):
        if not dry:
            os.remove(dest)
    elif os.path.isdir(dest):
        if not dry:
            shutil.rmtree(dest)
    if link:
        log(f"link  {dest} -> {KIT}", dry)
        if not dry:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            os.symlink(KIT, dest)
        return
    log(f"copy  {KIT} -> {dest}", dry)
    if dry:
        return
    os.makedirs(dest, exist_ok=True)
    for part in KIT_PARTS:
        src = os.path.join(KIT, part)
        if not os.path.exists(src):
            continue
        dst = os.path.join(dest, part)
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(src, dst)


def write(path: str, content: str, dry: bool):
    log(f"write {path}", dry)
    if dry:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------- Codex layout
def codex_skill_shim(cmd_md: str, kit_rel: str) -> str:
    name = os.path.splitext(os.path.basename(cmd_md))[0]
    desc = frontmatter_description(cmd_md) or f"sdd-kit lifecycle command {name}"
    return f"""---
name: {name}
description: "{desc} Invoke explicitly as ${name} [args]. Part of the sdd-kit Spec-Driven Development lifecycle."
---

# ${name}

This is the `/{name}` lifecycle command of **sdd-kit**, packaged as a Codex
skill. The kit root is `{kit_rel}/` (relative to the repo root; every
`reference/…`, `templates/…`, `scripts/…`, `config/…` path below lives there).

1. Read `{kit_rel}/commands/{name}.md` and follow it end to end. Treat the text
   after `${name}` in the user's message as `$ARGUMENTS`.
2. Agent roles it names (e.g. `feature-planner`, `sdd-guardian`) are defined in
   `{kit_rel}/agents/<role>.md`. If your harness can spawn a subagent, give it
   that file as its instructions; otherwise adopt the role yourself in a fresh,
   focused pass — a reviewer role must not see the author's reasoning.
3. The routing brain and standing rules are the `sdd-router` and
   `sdd-key-rules` skills; the fail-closed gates in
   `{kit_rel}/config/workflow.json` still apply.
"""


def codex_root_skill(kit_rel: str) -> str:
    return f"""---
name: sdd-kit
description: "The sdd-kit Spec-Driven Development kit itself — playbook, templates, agent roles, hook scripts, workflow config. Consulted by the sdd-* skills; rarely invoked directly. Use $sdd-router to start."
---

# sdd-kit (kit root)

This directory is the kit root for the sdd-* skills: `reference/` (playbook +
where-does-it-go), `templates/` (the six spec files), `agents/` (phase roles),
`commands/` (lifecycle), `config/workflow.json` (gates), `scripts/` (hooks,
doctor, grounding check). Start with `$sdd-router`; run
`python3 {kit_rel}/scripts/sdd_doctor.py` to verify enforcement is on.
"""


def codex_hooks(kit_rel_or_abs: str) -> dict:
    def entry(matcher, script):
        e = {"hooks": [{"type": "command",
                        "command": f'python3 "{kit_rel_or_abs}/scripts/{script}"',
                        "timeout": 20}]}
        if matcher:
            e["matcher"] = matcher
        return e
    return {"hooks": {ev: [entry(m, s) for m, s in items] for ev, items in HOOK_SCRIPTS.items()}}


def merge_hooks(existing_path: str, ours: dict) -> dict:
    try:
        existing = json.load(open(existing_path, encoding="utf-8"))
    except Exception:
        existing = {}
    hooks = existing.setdefault("hooks", {})
    for ev, entries in ours["hooks"].items():
        kept = [e for e in hooks.get(ev, []) if "sdd-kit" not in json.dumps(e) and
                "sdd_kit" not in json.dumps(e)]
        # drop any earlier sdd-kit entries (by script name) then append fresh ones
        kept = [e for e in kept if not any(s in json.dumps(e) for _, s in HOOK_SCRIPTS[ev])]
        hooks[ev] = kept + entries
    return existing


def agents_md_block(kit_rel: str) -> str:
    return f"""{AGENTS_START}
## Spec-Driven Development (sdd-kit)

This repo runs under **sdd-kit**. Specs live in `${{SDD_SPECS_DIR:-specs}}/`
(Constitution: `domain-spec.md`, `engineering-spec.md`, `roadmap.md`; one dated
dir per feature with `requirements.md`, `plan.md`, `validation.md`, `samples/`).

- Start every SDD task with the `$sdd-router` skill; lifecycle: `$sdd-constitution`
  → `$sdd-plan` → `$sdd-implement` → `$sdd-validate` → `$sdd-replan`; health: `$sdd-doctor`.
- Hard rules (`$sdd-key-rules`): spec before code; commit the spec first; ground
  every data-dependent decision in a real captured sample; prove "done" on real
  data, not mocks; audit the goal noun-by-noun; recommend, never a neutral menu.
- Hooks in `.codex/hooks.json` enforce spec-before-code deterministically; the
  kit root is `{kit_rel}/`.
{AGENTS_END}
"""


def install_codex(project: str, scope: str, link: bool, dry: bool):
    if scope == "user":
        base = os.path.expanduser("~/.agents/skills")
        hooks_path = os.path.expanduser("~/.codex/hooks.json")
        kit_dest = os.path.join(base, "sdd-kit")
        kit_ref = kit_dest  # absolute in user-scope hooks
    else:
        base = os.path.join(project, ".agents", "skills")
        hooks_path = os.path.join(project, ".codex", "hooks.json")
        kit_dest = os.path.join(base, "sdd-kit")
        kit_ref = ".agents/skills/sdd-kit"

    copy_kit(kit_dest, link, dry)
    write(os.path.join(kit_dest, "SKILL.md"), codex_root_skill(kit_ref), dry) if not link else None

    # rules/router skills at the top level so Codex discovers them
    for name in sorted(os.listdir(os.path.join(KIT, "skills"))):
        src = os.path.join(KIT, "skills", name, "SKILL.md")
        if os.path.isfile(src):
            write(os.path.join(base, name, "SKILL.md"), open(src, encoding="utf-8").read(), dry)
    # one shim skill per lifecycle command → $sdd-plan etc.
    for f in sorted(os.listdir(os.path.join(KIT, "commands"))):
        if f.endswith(".md"):
            name = f[:-3]
            write(os.path.join(base, name, "SKILL.md"),
                  codex_skill_shim(os.path.join(KIT, "commands", f), kit_ref), dry)

    merged = merge_hooks(hooks_path, codex_hooks(kit_ref))
    write(hooks_path, json.dumps(merged, indent=2) + "\n", dry)

    if scope == "project":
        agents_md = os.path.join(project, "AGENTS.md")
        block = agents_md_block(kit_ref)
        text = open(agents_md, encoding="utf-8").read() if os.path.isfile(agents_md) else ""
        if AGENTS_START in text and AGENTS_END in text:
            text = re.sub(re.escape(AGENTS_START) + r".*?" + re.escape(AGENTS_END) + r"\n?",
                          block, text, flags=re.DOTALL)
        else:
            text = (text.rstrip() + "\n\n" if text.strip() else "") + block
        write(agents_md, text, dry)
    print(f"\nCodex: skills in {base}/ (use $sdd-router), hooks in {hooks_path}."
          f"\n       Restart Codex so it re-scans skills/hooks; project hooks load once the repo is trusted.")


# ---------------------------------------------------------- Claude Code layout
def install_claude(project: str, scope: str, link: bool, dry: bool):
    if scope == "user":
        dest = os.path.expanduser("~/.claude/skills/sdd-kit")
    else:
        dest = os.path.join(project, ".claude", "skills", "sdd-kit")
    copy_kit(dest, link, dry)
    print(f"\nClaude Code: vendored at {dest} (auto-loads as a skills-dir plugin, hooks included)."
          f"\n             Marketplace alternative: /plugin marketplace add blutrich/sdd-kit && /plugin install sdd-kit@sdd-kit")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harness", choices=("claude", "codex", "both"), default="both")
    ap.add_argument("--scope", choices=("project", "user"), default="project")
    ap.add_argument("--project", default=os.getcwd(), help="project dir (default: cwd)")
    ap.add_argument("--link", action="store_true", help="symlink the kit instead of copying (local dev)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    project = os.path.abspath(a.project)
    print(f"sdd-kit installer — kit {KIT}\nproject {project}  harness={a.harness}  scope={a.scope}\n")
    if a.harness in ("claude", "both"):
        install_claude(project, a.scope, a.link, a.dry_run)
    if a.harness in ("codex", "both"):
        install_codex(project, a.scope, a.link, a.dry_run)
    print("\nNext: run the doctor —  python3 <kit>/scripts/sdd_doctor.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
