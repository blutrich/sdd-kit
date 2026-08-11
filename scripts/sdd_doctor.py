#!/usr/bin/env python3
"""sdd-doctor — verify the kit is actually installed, loaded, and enforceable.

The failure mode this closes: the hooks fail OPEN by design, so a missing
python3, a stale plugin cache, or an unresolvable plugin root produces a kit
that *looks* installed and enforces nothing. This script makes that state
visible in one run. Read-only; safe anywhere.

Usage:  python3 sdd_doctor.py [project-dir]     (default: cwd)
Exit:   0 = healthy, 1 = at least one ❌.
"""
import json
import os
import py_compile
import re
import subprocess
import sys

KIT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OK, BAD, WARN = "✅", "❌", "⚠️ "


def git(args, cwd):
    try:
        r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def main() -> int:
    cwd = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    cwd = os.path.abspath(cwd)
    failures = 0

    def report(ok, label, detail=""):
        nonlocal failures
        mark = OK if ok else BAD
        if not ok:
            failures += 1
        print(f"{mark} {label}" + (f" — {detail}" if detail else ""))

    def warn(label, detail=""):
        print(f"{WARN}{label}" + (f" — {detail}" if detail else ""))

    print("SDD DOCTOR\n==========")

    # 1 · Interpreter
    py = sys.version_info
    report(py >= (3, 9), f"python3 is {py.major}.{py.minor}.{py.micro}",
           "" if py >= (3, 9) else "hooks need Python ≥ 3.9")

    # 2 · Kit version + hook scripts compile
    version = "?"
    plugin_json = os.path.join(KIT_ROOT, ".claude-plugin", "plugin.json")
    try:
        version = json.load(open(plugin_json)).get("version", "?")
        report(True, f"kit at {KIT_ROOT} (v{version})")
    except Exception as e:
        report(False, "plugin.json unreadable", str(e))
    for script in ("inject_constitution.py", "spec_before_code_guard.py",
                   "bash_write_guard.py", "check_grounding.py"):
        path = os.path.join(KIT_ROOT, "scripts", script)
        try:
            py_compile.compile(path, doraise=True)
            report(True, f"scripts/{script} compiles")
        except Exception as e:
            report(False, f"scripts/{script} broken", str(e))

    # 3 · Stale-cache check (the most common silent failure on real machines)
    cache_root = os.path.expanduser("~/.claude/plugins/cache/sdd-kit/sdd-kit")
    if os.path.isdir(cache_root):
        cached = sorted(os.listdir(cache_root))
        if cached and not any(v == version for v in cached):
            report(False, f"installed plugin cache is {'/'.join(cached)} but this kit is v{version}",
                   "run /plugin update sdd-kit")
        elif cached:
            report(True, f"plugin cache matches (v{version})")

    # 4 · Project state
    specs_rel = (os.environ.get("SDD_SPECS_DIR", "specs") or "specs").strip().strip("/")
    root = git(["rev-parse", "--show-toplevel"], cwd) or cwd
    print(f"\nProject: {root}  (specs dir: {specs_rel}/)")
    domain = os.path.join(root, specs_rel, "domain-spec.md")
    if not os.path.isfile(domain):
        warn("no Constitution", f"{specs_rel}/domain-spec.md missing — the kit is INERT here. "
             "Run /sdd-constitution to switch it on.")
        print("\nVERDICT:", "HEALTHY (kit ok, project not under SDD)" if failures == 0 else f"{failures} problem(s)")
        return 1 if failures else 0
    for f in ("domain-spec.md", "engineering-spec.md", "roadmap.md"):
        report(os.path.isfile(os.path.join(root, specs_rel, f)), f"{specs_rel}/{f}")

    # 5 · Guard mode + branch↔spec contract
    mode = os.environ.get("SDD_GUARD", "block").lower()
    if mode in ("off", "0", "false", "none"):
        warn(f"SDD_GUARD={mode}", "enforcement DISABLED in this shell")
    elif mode in ("warn", "advisory", "soft"):
        warn(f"SDD_GUARD={mode}", "advisory only — the gate will not block")
    elif mode == "block":
        report(True, "SDD_GUARD=block (fail-closed)")
    else:
        warn(f"SDD_GUARD={mode}", "unrecognized value → treated as block")

    branch = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    sys.path.insert(0, os.path.join(KIT_ROOT, "scripts"))
    try:
        from spec_before_code_guard import resolve_spec, spec_candidates  # noqa: E402
        spec_name, _ = resolve_spec(root, branch)
        if branch in ("main", "master"):
            warn(f"on '{branch}'", "code edits are blocked here by design — implement on a feature branch")
        elif spec_name:
            report(True, f"branch '{branch}' → {specs_rel}/{spec_name}/")
        else:
            looked = ", ".join(spec_candidates(branch)) or "(none)"
            warn(f"branch '{branch}' resolves to no spec", f"candidates tried: {looked} — "
                 "code edits will be blocked until /sdd-plan creates one")
    except Exception as e:
        report(False, "guard import failed", str(e))

    print("\nVERDICT:", "HEALTHY" if failures == 0 else f"{failures} problem(s) — fix the ❌ lines above")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
