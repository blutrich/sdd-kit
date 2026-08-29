#!/usr/bin/env python3
"""Tests for the sdd-kit hook scripts — run against REAL temp git repos (KR13:
the scripts are exercised through their actual stdin/stdout contract via
subprocess, not by mocking both ends).

Run:  python3 -m unittest discover -s tests -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(KIT, "scripts")
GUARD = os.path.join(SCRIPTS, "spec_before_code_guard.py")
BASH_GUARD = os.path.join(SCRIPTS, "bash_write_guard.py")
GROUNDING = os.path.join(SCRIPTS, "check_grounding.py")

sys.path.insert(0, SCRIPTS)
import inject_constitution  # noqa: E402


def sh(args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


class RepoCase(unittest.TestCase):
    """A temp git repo per test, with helpers to build SDD state."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        sh(["git", "init", "-q", "-b", "main"], self.root)
        sh(["git", "config", "user.email", "t@t"], self.root)
        sh(["git", "config", "user.name", "t"], self.root)

    def tearDown(self):
        self.tmp.cleanup()

    # -- builders ------------------------------------------------------------
    def write(self, rel, content="x\n"):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return path

    def commit_all(self, msg="c"):
        sh(["git", "add", "-A"], self.root)
        sh(["git", "commit", "-qm", msg], self.root)

    def constitution(self):
        self.write("specs/domain-spec.md", "# domain\n")
        self.commit_all("constitution")

    def spec(self, name, committed=True):
        self.write(f"specs/{name}/requirements.md", "# req\n")
        if committed:
            self.commit_all(f"spec {name}")

    def branch(self, name):
        sh(["git", "checkout", "-qb", name], self.root)

    # -- runners -------------------------------------------------------------
    def run_guard(self, file_path, env=None, script=GUARD, tool_input=None):
        payload = {
            "tool_input": tool_input or {"file_path": os.path.join(self.root, file_path)},
            "cwd": self.root,
        }
        full_env = dict(os.environ)
        full_env.pop("SDD_GUARD", None)
        full_env.pop("SDD_SPECS_DIR", None)
        if env:
            full_env.update(env)
        r = subprocess.run(
            [sys.executable, script], input=json.dumps(payload),
            capture_output=True, text=True, env=full_env, timeout=30,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)["hookSpecificOutput"] if r.stdout.strip() else None


class TestGuardScope(RepoCase):
    def test_markdown_is_exempt(self):
        self.constitution()
        self.assertIsNone(self.run_guard("notes.md"))

    def test_no_constitution_is_inert(self):
        self.assertIsNone(self.run_guard("src/app.py"))

    def test_tests_dir_is_exempt(self):  # A4: dir-aware
        self.constitution()
        self.assertIsNone(self.run_guard("tests/helpers.py"))
        self.assertIsNone(self.run_guard("src/__tests__/setup.js"))

    def test_test_basenames_are_exempt(self):  # A4
        self.constitution()
        self.assertIsNone(self.run_guard("src/foo.test.ts"))
        self.assertIsNone(self.run_guard("src/test_foo.py"))
        self.assertIsNone(self.run_guard("src/conftest.py"))

    def test_test_substring_is_not_exempt(self):  # A4: 'latest.ts' is code
        self.constitution()
        self.branch("nospec")
        out = self.run_guard("src/latest.ts")
        self.assertEqual(out.get("permissionDecision"), "deny")

    def test_shell_and_sql_are_code(self):  # A6
        self.constitution()
        self.branch("nospec")
        for f in ("deploy.sh", "migrate.sql", "App.vue"):
            out = self.run_guard(f"src/{f}")
            self.assertEqual(out.get("permissionDecision"), "deny", f)


class TestGuardResolution(RepoCase):
    def test_exact_branch_spec_allows(self):
        self.constitution()
        self.branch("2026-08-11-thing")
        self.spec("2026-08-11-thing")
        self.assertIsNone(self.run_guard("src/app.py"))

    def test_slashed_branch_resolves_last_segment(self):  # A1 — the 4×-recurring bug
        self.constitution()
        self.spec("2026-08-11-thing")
        self.branch("spec/2026-08-11-thing")
        self.assertIsNone(self.run_guard("src/app.py"))

    def test_slashed_branch_resolves_slug(self):  # A1
        self.constitution()
        self.spec("feat-2026-08-11-thing")
        self.branch("feat/2026-08-11-thing")
        self.assertIsNone(self.run_guard("src/app.py"))

    def test_no_spec_names_candidates(self):
        self.constitution()
        self.branch("spec/xyz")
        out = self.run_guard("src/app.py")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("specs/xyz/", out["permissionDecisionReason"])

    def test_main_gets_specific_message(self):  # A3
        self.constitution()
        out = self.run_guard("src/app.py")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("feature branch", out["permissionDecisionReason"])
        self.assertIn("hotfix", out["permissionDecisionReason"])

    def test_uncommitted_spec_blocks_with_kr4(self):  # A5
        self.constitution()
        self.branch("2026-08-11-thing")
        self.spec("2026-08-11-thing", committed=False)
        out = self.run_guard("src/app.py")
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("not committed", out["permissionDecisionReason"])


class TestGuardModes(RepoCase):
    def test_warn_is_advisory(self):
        self.constitution()
        self.branch("nospec")
        out = self.run_guard("src/app.py", env={"SDD_GUARD": "warn"})
        self.assertIn("additionalContext", out)
        self.assertNotIn("permissionDecision", out)

    def test_off_is_silent(self):
        self.constitution()
        self.branch("nospec")
        self.assertIsNone(self.run_guard("src/app.py", env={"SDD_GUARD": "off"}))

    def test_garbage_stdin_fails_open(self):
        r = subprocess.run([sys.executable, GUARD], input="{not json",
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


class TestHarnessAgnostic(RepoCase):
    """Codex speaks the same hook contract with different names: PLUGIN_ROOT,
    apply_patch payloads, no CLAUDE_PROJECT_DIR."""

    def test_apply_patch_payload_is_gated(self):
        self.constitution()
        self.branch("nospec")
        patch = "*** Begin Patch\n*** Add File: src/app.py\n+print(1)\n*** End Patch\n"
        out = self.run_guard(None, tool_input={"patch": patch})
        self.assertEqual(out.get("permissionDecision"), "deny")
        self.assertIn("src/app.py", out["permissionDecisionReason"])

    def test_apply_patch_docs_only_passes(self):
        self.constitution()
        self.branch("nospec")
        patch = "*** Begin Patch\n*** Update File: README.md\n@@\n+x\n*** End Patch\n"
        self.assertIsNone(self.run_guard(None, tool_input={"patch": patch}))

    def test_apply_patch_with_spec_passes(self):
        self.constitution()
        self.branch("2026-08-29-thing")
        self.spec("2026-08-29-thing")
        patch = "*** Begin Patch\n*** Update File: src/app.py\n@@\n+x\n*** End Patch\n"
        self.assertIsNone(self.run_guard(None, tool_input={"patch": patch}))

    def test_codex_env_and_cwd_only(self):  # no CLAUDE_* vars at all
        self.constitution()
        self.branch("nospec")
        env = {"PLUGIN_ROOT": KIT, "SDD_HARNESS": "codex"}
        out = self.run_guard("src/app.py", env=env)
        self.assertEqual(out.get("permissionDecision"), "deny")

    def test_agents_dirs_exempt(self):
        self.constitution()
        self.branch("nospec")
        self.assertIsNone(self.run_guard(".agents/skills/x/scripts/run.py"))
        self.assertIsNone(self.run_guard(".codex/tool.py"))


class TestBashGuard(RepoCase):
    def run_bash(self, command, env=None):
        return self.run_guard(None, env=env, script=BASH_GUARD,
                              tool_input={"command": command})

    def test_heredoc_to_code_is_flagged(self):  # A2
        self.constitution()
        self.branch("nospec")
        out = self.run_bash("cat > src/app.py <<'EOF'\nprint(1)\nEOF")
        self.assertIn("additionalContext", out)
        self.assertIn("app.py", out["additionalContext"])
        self.assertNotIn("permissionDecision", out)  # advisory ONLY

    def test_plain_command_is_silent(self):
        self.constitution()
        self.branch("nospec")
        self.assertIsNone(self.run_bash("ls -la && git status"))

    def test_spec_branch_is_silent(self):
        self.constitution()
        self.branch("2026-08-11-thing")
        self.spec("2026-08-11-thing")
        self.assertIsNone(self.run_bash("echo hi > src/app.py"))


class TestInjectorRoadmap(unittest.TestCase):
    def _roadmap(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(text)
            return f.name

    def test_first_unchecked_phase(self):
        p = self._roadmap("## Phase 1: A\n- [x] done\n\n## Phase 2: B\n- [ ] todo\n")
        self.assertEqual(inject_constitution.first_unchecked_phase(p), "Phase 2: B")

    def test_notes_section_is_ignored(self):  # phase-aware fix
        p = self._roadmap("## Phase 1: A\n**Status:** ✅ done\n- [x] d\n\n## Notes\n- [ ] someday\n")
        self.assertIsNone(inject_constitution.first_unchecked_phase(p))

    def test_status_pending_matches(self):
        p = self._roadmap("## Phase 1: A\n**Status:** ⬜ pending\n")
        self.assertEqual(inject_constitution.first_unchecked_phase(p), "Phase 1: A")


class TestInjectorOutput(RepoCase):
    def run_inject(self, env):
        full = dict(os.environ)
        for k in ("SDD_HOOK_FORMAT", "CLAUDE_PROJECT_DIR"):
            full.pop(k, None)
        full.update(env)
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "inject_constitution.py")],
                           input=json.dumps({"cwd": self.root}), capture_output=True,
                           text=True, env=full, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_json_by_default_uses_payload_cwd(self):
        self.constitution()
        out = json.loads(self.run_inject({}))
        self.assertIn("Spec-Driven", out["hookSpecificOutput"]["additionalContext"])

    def test_text_mode(self):
        self.constitution()
        out = self.run_inject({"SDD_HOOK_FORMAT": "text"})
        self.assertIn("Spec-Driven", out)
        self.assertFalse(out.lstrip().startswith("{"))


class TestInstaller(RepoCase):
    def test_codex_project_layout(self):
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "sdd_install.py"),
                            "--harness", "codex", "--project", self.root],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        skills = os.path.join(self.root, ".agents", "skills")
        for name in ("sdd-router", "sdd-key-rules", "sdd-plan", "sdd-doctor", "sdd-kit"):
            self.assertTrue(os.path.isfile(os.path.join(skills, name, "SKILL.md")), name)
        self.assertTrue(os.path.isfile(os.path.join(skills, "sdd-kit", "scripts", "spec_before_code_guard.py")))
        hooks = json.load(open(os.path.join(self.root, ".codex", "hooks.json")))
        self.assertIn("apply_patch", hooks["hooks"]["PreToolUse"][0]["matcher"])
        agents = open(os.path.join(self.root, "AGENTS.md")).read()
        self.assertIn("$sdd-router", agents)
        # idempotent: second run does not duplicate the AGENTS.md block or hooks
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "sdd_install.py"),
                        "--harness", "codex", "--project", self.root], check=True, capture_output=True)
        self.assertEqual(open(os.path.join(self.root, "AGENTS.md")).read().count("sdd-kit:start"), 1)
        hooks = json.load(open(os.path.join(self.root, ".codex", "hooks.json")))
        self.assertEqual(len(hooks["hooks"]["PreToolUse"]), 2)

    def test_claude_project_layout(self):
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "sdd_install.py"),
                            "--harness", "claude", "--project", self.root],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(
            self.root, ".claude", "skills", "sdd-kit", ".claude-plugin", "plugin.json")))


class TestGrounding(unittest.TestCase):
    def run_check(self, feature_dir):
        return subprocess.run([sys.executable, GROUNDING, feature_dir],
                              capture_output=True, text=True, timeout=30)

    def test_missing_samples_fails(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "requirements.md"), "w").write("# r\n")
            r = self.run_check(d)
            self.assertEqual(r.returncode, 1)
            self.assertIn("no captured samples", r.stdout)

    def test_provenance_passes(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "requirements.md"), "w").write("# r\n")
            os.makedirs(os.path.join(d, "samples"))
            open(os.path.join(d, "samples", "api.json"), "w").write(
                "// captured 2026-08-11 via: curl https://api.example.com/v1/x\n{}\n")
            r = self.run_check(d)
            self.assertEqual(r.returncode, 0, r.stdout)

    def test_no_provenance_fails(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "requirements.md"), "w").write("# r\n")
            os.makedirs(os.path.join(d, "samples"))
            open(os.path.join(d, "samples", "api.json"), "w").write('{"a": 1}\n')
            r = self.run_check(d)
            self.assertEqual(r.returncode, 1)
            self.assertIn("provenance", r.stdout)


if __name__ == "__main__":
    unittest.main()
