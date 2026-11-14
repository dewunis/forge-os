from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("forgeos_installer", ROOT / "scripts" / "forgeos.py")
assert SPEC and SPEC.loader
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)


class InstallerTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            result = INSTALLER.main(list(arguments))
        return result, output.getvalue()

    def assert_counts(self, root: Path, tool: str) -> None:
        if tool in {"codex", "all"}:
            self.assertEqual(17, len(list((root / ".codex" / "agents").glob("*.toml"))))
            self.assertEqual(16, len(list((root / ".agents" / "skills").glob("*/SKILL.md"))))
            self.assertFalse((root / ".codex" / "config.toml").exists())
        if tool in {"claude", "all"}:
            self.assertEqual(17, len(list((root / ".claude" / "agents").glob("*.md"))))
            self.assertEqual(16, len(list((root / ".claude" / "skills").glob("*/SKILL.md"))))
            self.assertFalse((root / ".claude" / "settings.json").exists())

    def test_local_all_lifecycle_is_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "projet é avec espaces"
            target.mkdir()
            sentinel = target / "application.txt"
            sentinel.write_text("keep", encoding="utf-8")
            common = ("--tool", "all", "--scope", "local", "--target", str(target))

            self.assertEqual(0, self.run_cli("install", *common)[0])
            self.assert_counts(target, "all")
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertEqual(0, self.run_cli("status", *common)[0])
            self.assertEqual(0, self.run_cli("update", *common)[0])
            self.assertEqual(0, self.run_cli("uninstall", *common)[0])
            self.assertEqual("keep", sentinel.read_text(encoding="utf-8"))
            self.assertFalse((target / ".forgeos" / "install-manifest.json").exists())

    def test_global_tool_selections_use_only_injected_home(self) -> None:
        for tool in ("codex", "claude", "all"):
            with self.subTest(tool=tool), tempfile.TemporaryDirectory() as temporary:
                home = Path(temporary) / "home"
                home.mkdir()
                common = ("--tool", tool, "--scope", "global", "--home", str(home))
                self.assertEqual(0, self.run_cli("install", *common)[0])
                self.assert_counts(home, tool)
                self.assertTrue((home / ".forgeos" / "AGENTS.md").is_file())
                if tool == "codex":
                    self.assertTrue((home / ".codex" / "AGENTS.md").is_file())
                    self.assertFalse((home / ".claude").exists())
                elif tool == "claude":
                    self.assertTrue((home / ".claude" / "CLAUDE.md").is_file())
                    self.assertFalse((home / ".codex").exists())
                    self.assertFalse((home / ".agents").exists())
                    claude_entry = (home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
                    self.assertIn("@../.forgeos/AGENTS.md", claude_entry)
                    self.assertNotIn(".codex/agents/*.toml", claude_entry)
                    self.assertNotIn(".agents/skills/*/SKILL.md", claude_entry)
                    self.assertNotIn("claude_adapter.py", claude_entry)
                    claude_agent = (home / ".claude" / "agents" / "frontend-engineer.md").read_text(encoding="utf-8")
                    self.assertIn((home / ".claude" / "skills").as_posix(), claude_agent)
                    self.assertNotIn(".agents/skills/", claude_agent)
                    canonical_agent = (home / ".forgeos" / "sources" / "agents" / "frontend-engineer.toml").read_text(encoding="utf-8")
                    self.assertIn((home / ".claude" / "skills").as_posix(), canonical_agent)
                self.assertEqual(0, self.run_cli("status", *common)[0])
                self.assertEqual(0, self.run_cli("uninstall", *common)[0])

    def test_conflict_requires_backup_and_uninstall_restores_original(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            existing = target / "AGENTS.md"
            existing.write_text("original project instructions\n", encoding="utf-8")
            common = ("--tool", "codex", "--scope", "local", "--target", str(target))

            self.assertEqual(1, self.run_cli("install", *common)[0])
            self.assertEqual("original project instructions\n", existing.read_text(encoding="utf-8"))
            self.assertEqual(0, self.run_cli("install", *common, "--conflict", "backup")[0])
            self.assertNotEqual("original project instructions\n", existing.read_text(encoding="utf-8"))
            self.assertEqual(0, self.run_cli("uninstall", *common)[0])
            self.assertEqual("original project instructions\n", existing.read_text(encoding="utf-8"))

    def test_drift_blocks_status_update_and_uninstall_without_data_loss(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            sentinel = target / "sentinel.txt"
            sentinel.write_text("outside ownership", encoding="utf-8")
            common = ("--tool", "codex", "--scope", "local", "--target", str(target))
            self.assertEqual(0, self.run_cli("install", *common)[0])
            agent = target / ".codex" / "agents" / "frontend-engineer.toml"
            installed = agent.read_bytes()
            agent.write_text("user modification", encoding="utf-8")

            self.assertEqual(1, self.run_cli("status", *common)[0])
            self.assertEqual(1, self.run_cli("update", *common)[0])
            self.assertEqual("user modification", agent.read_text(encoding="utf-8"))
            self.assertEqual(1, self.run_cli("uninstall", *common)[0])
            self.assertEqual("user modification", agent.read_text(encoding="utf-8"))
            self.assertEqual("outside ownership", sentinel.read_text(encoding="utf-8"))

            agent.parent.mkdir(parents=True, exist_ok=True)
            agent.write_bytes(installed)
            self.assertEqual(0, self.run_cli("uninstall", *common)[0])
            self.assertEqual("outside ownership", sentinel.read_text(encoding="utf-8"))

    def test_settings_require_explicit_option(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            common = (
                "--tool", "all", "--scope", "local", "--target", str(target),
                "--include-settings",
            )
            self.assertEqual(0, self.run_cli("install", *common)[0])
            self.assertTrue((target / ".codex" / "config.toml").is_file())
            self.assertTrue((target / ".claude" / "settings.json").is_file())
            self.assertEqual(0, self.run_cli("uninstall", *common)[0])

    def test_wrong_tool_cannot_inspect_or_uninstall_an_all_installation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            all_args = ("--tool", "all", "--scope", "local", "--target", str(target))
            claude_args = ("--tool", "claude", "--scope", "local", "--target", str(target))
            self.assertEqual(0, self.run_cli("install", *all_args)[0])
            manifest = target / ".forgeos" / "install-manifest.json"
            before = manifest.read_bytes()

            self.assertEqual(1, self.run_cli("status", *claude_args)[0])
            self.assertEqual(1, self.run_cli("uninstall", *claude_args)[0])
            self.assertEqual(before, manifest.read_bytes())
            self.assertTrue((target / ".codex" / "agents" / "frontend-engineer.toml").is_file())
            self.assertTrue((target / ".claude" / "agents" / "frontend-engineer.md").is_file())
            self.assertEqual(0, self.run_cli("status", *all_args)[0])
            self.assertEqual(0, self.run_cli("uninstall", *all_args)[0])

    def test_update_snapshot_does_not_replace_preinstall_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            instructions = target / "AGENTS.md"
            instructions.write_text("before ForgeOS\n", encoding="utf-8")
            common = ("--tool", "codex", "--scope", "local", "--target", str(target))
            self.assertEqual(0, self.run_cli("install", *common, "--conflict", "backup")[0])
            manifest_path = target / ".forgeos" / "install-manifest.json"
            manifest_before = json.loads(manifest_path.read_text(encoding="utf-8"))
            original_backup = manifest_before["files"]["AGENTS.md"]["backup"]
            instructions.write_text("locally changed after install\n", encoding="utf-8")

            self.assertEqual(0, self.run_cli("update", *common, "--conflict", "backup")[0])
            manifest_after = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(original_backup, manifest_after["files"]["AGENTS.md"]["backup"])
            snapshots = manifest_after.get("update_snapshots", [])
            self.assertTrue(snapshots)
            self.assertTrue(any((target / Path(name)).is_file() for name in snapshots))
            uninstall_code, uninstall_output = self.run_cli("uninstall", *common)
            self.assertEqual(0, uninstall_code)
            self.assertIn("recovery snapshots preserved", uninstall_output)
            self.assertEqual("before ForgeOS\n", instructions.read_text(encoding="utf-8"))

    def test_scope_specific_path_options_are_rejected_and_absent_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(
                1,
                self.run_cli(
                    "install", "--scope", "global", "--home", str(root),
                    "--target", str(root / "project"),
                )[0],
            )
            self.assertEqual(
                1,
                self.run_cli(
                    "install", "--scope", "local", "--target", str(root),
                    "--home", str(root / "home"),
                )[0],
            )
            code, output = self.run_cli(
                "status", "--scope", "local", "--target", str(root), "--tool", "all"
            )
            self.assertEqual(0, code)
            self.assertIn("ABSENT", output)
            self.assertEqual([], list(root.iterdir()))

    def test_manifest_path_traversal_is_rejected_without_touching_outside_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            outside = Path(temporary) / "outside.txt"
            outside.write_text("keep", encoding="utf-8")
            common = ("--tool", "codex", "--scope", "local", "--target", str(target))
            self.assertEqual(0, self.run_cli("install", *common)[0])
            manifest_path = target / ".forgeos" / "install-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"]["../outside.txt"] = {"sha256": "0" * 64}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            self.assertEqual(1, self.run_cli("uninstall", *common)[0])
            self.assertEqual("keep", outside.read_text(encoding="utf-8"))

    def test_manifest_backup_traversal_is_rejected_without_touching_outside_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            outside = Path(temporary) / "outside.txt"
            outside.write_text("keep", encoding="utf-8")
            common = ("--tool", "codex", "--scope", "local", "--target", str(target))
            self.assertEqual(0, self.run_cli("install", *common)[0])
            manifest_path = target / ".forgeos" / "install-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"]["AGENTS.md"]["backup"] = (
                ".forgeos/backups/../../outside.txt"
            )
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            self.assertEqual(1, self.run_cli("uninstall", *common)[0])
            self.assertEqual("keep", outside.read_text(encoding="utf-8"))

    def test_update_restores_preinstallation_backup_when_owned_file_becomes_obsolete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            instructions = target / "AGENTS.md"
            instructions.write_text("original governance\n", encoding="utf-8")
            common = ("--tool", "codex", "--scope", "local", "--target", str(target))
            self.assertEqual(0, self.run_cli("install", *common, "--conflict", "backup")[0])
            original_builder = INSTALLER.build_plan

            def without_instructions(args, base, shared):
                plan = original_builder(args, base, shared)
                plan.pop(base / "AGENTS.md")
                return plan

            with mock.patch.object(INSTALLER, "build_plan", side_effect=without_instructions):
                self.assertEqual(0, self.run_cli("update", *common)[0])

            self.assertEqual("original governance\n", instructions.read_text(encoding="utf-8"))
            manifest = json.loads(
                (target / ".forgeos" / "install-manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertNotIn("AGENTS.md", manifest["files"])
            self.assertEqual(0, self.run_cli("uninstall", *common)[0])
            self.assertEqual("original governance\n", instructions.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
