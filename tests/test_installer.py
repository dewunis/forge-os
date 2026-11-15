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


def _load_script_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INSTALLER = _load_script_module("forgeos_installer", ROOT / "scripts" / "forgeos.py")
GEMINI_ADAPTER = _load_script_module("gemini_adapter", ROOT / "scripts" / "gemini_adapter.py")


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
        if tool in {"gemini", "all"}:
            self.assertEqual(17, len(list((root / ".gemini" / "agents").glob("*.md"))))
            self.assertEqual(17, len(list((root / ".gemini" / "antigravity-agents").glob("*.md"))))
            self.assertEqual(16, len(list((root / ".gemini" / "skills").glob("*/SKILL.md"))))
            self.assertFalse((root / ".gemini" / "settings.json").exists())

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

    def test_local_gemini_lifecycle_is_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "projet gemini"
            target.mkdir()
            common = ("--tool", "gemini", "--scope", "local", "--target", str(target))

            self.assertEqual(0, self.run_cli("install", *common)[0])
            self.assert_counts(target, "gemini")
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertTrue((target / ".gemini" / "GEMINI.md").is_file())
            self.assertFalse((target / ".codex").exists())
            self.assertFalse((target / ".claude").exists())
            self.assertTrue((target / ".agents" / "agents.json").is_file())
            self.assertTrue((target / ".agents" / "skills.json").is_file())
            self.assertFalse((target / ".agents" / "skills").exists())
            self.assertEqual(
                {"entries": [{"path": ".gemini/antigravity-agents"}]},
                json.loads((target / ".agents" / "agents.json").read_text(encoding="utf-8")),
            )
            self.assertEqual(
                {"entries": [{"path": ".gemini/skills"}]},
                json.loads((target / ".agents" / "skills.json").read_text(encoding="utf-8")),
            )
            governance = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn(".gemini/skills/*/SKILL.md", governance)
            self.assertNotIn("gemini_adapter.py", governance)
            gemini_entry = (target / ".gemini" / "GEMINI.md").read_text(encoding="utf-8")
            self.assertIn("@../AGENTS.md", gemini_entry)
            self.assertNotIn("gemini_adapter.py", gemini_entry)
            self.assertEqual(0, self.run_cli("status", *common)[0])
            self.assertEqual(0, self.run_cli("update", *common)[0])
            self.assertEqual(0, self.run_cli("uninstall", *common)[0])
            self.assertFalse((target / ".forgeos" / "install-manifest.json").exists())

    def test_global_tool_selections_use_only_injected_home(self) -> None:
        isolated_adapters = {
            "claude": ("CLAUDE.md", "claude_adapter.py", ".gemini"),
            "gemini": ("GEMINI.md", "gemini_adapter.py", ".claude"),
        }
        for tool in ("codex", "claude", "gemini", "all"):
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
                    self.assertFalse((home / ".gemini").exists())
                elif tool in isolated_adapters:
                    entry_name, adapter_script, other_dir = isolated_adapters[tool]
                    entry_path = home / f".{tool}" / entry_name
                    self.assertTrue(entry_path.is_file())
                    self.assertFalse((home / ".codex").exists())
                    self.assertFalse((home / ".agents").exists())
                    self.assertFalse((home / other_dir).exists())
                    entry = entry_path.read_text(encoding="utf-8")
                    self.assertIn("@../.forgeos/AGENTS.md", entry)
                    self.assertNotIn(".codex/agents/*.toml", entry)
                    self.assertNotIn(".agents/skills/*/SKILL.md", entry)
                    self.assertNotIn(adapter_script, entry)
                    adapter_agent = (home / f".{tool}" / "agents" / "frontend-engineer.md").read_text(encoding="utf-8")
                    self.assertIn((home / f".{tool}" / "skills").as_posix(), adapter_agent)
                    self.assertNotIn(".agents/skills/", adapter_agent)
                    canonical_agent = (home / ".forgeos" / "sources" / "agents" / "frontend-engineer.toml").read_text(encoding="utf-8")
                    self.assertIn((home / f".{tool}" / "skills").as_posix(), canonical_agent)
                    if tool == "gemini":
                        config_root = home / ".gemini" / "config"
                        self.assertTrue((config_root / "GEMINI.md").is_file())
                        self.assertTrue((config_root / "agents.json").is_file())
                        self.assertTrue((config_root / "skills.json").is_file())
                        self.assertIn(
                            "@../../.forgeos/AGENTS.md",
                            (config_root / "GEMINI.md").read_text(encoding="utf-8"),
                        )
                        self.assertEqual(
                            {"entries": [{"path": (home / ".gemini" / "antigravity-agents").as_posix()}]},
                            json.loads((config_root / "agents.json").read_text(encoding="utf-8")),
                        )
                        self.assertEqual(
                            {"entries": [{"path": (home / ".gemini" / "skills").as_posix()}]},
                            json.loads((config_root / "skills.json").read_text(encoding="utf-8")),
                        )
                        ag_agent = (
                            home / ".gemini" / "antigravity-agents" / "frontend-engineer.md"
                        ).read_text(encoding="utf-8")
                        self.assertIn((home / ".gemini" / "skills").as_posix(), ag_agent)
                        self.assertIn("../skills/frontend-development", ag_agent)
                        self.assertNotIn(".agents/skills/", ag_agent)
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
            self.assertTrue((target / ".gemini" / "settings.json").is_file())
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
            self.assertTrue((target / ".gemini" / "agents" / "frontend-engineer.md").is_file())
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


class GeminiAdapterTests(unittest.TestCase):
    def test_role_classification_is_exhaustive_and_rejects_unknown_role(self) -> None:
        canonical_stems = {path.stem for path in GEMINI_ADAPTER.canonical_agent_files()}
        self.assertEqual(17, len(canonical_stems))
        self.assertFalse(GEMINI_ADAPTER.READ_ONLY_AGENTS & GEMINI_ADAPTER.READ_WRITE_AGENTS)
        self.assertEqual(
            canonical_stems,
            GEMINI_ADAPTER.READ_ONLY_AGENTS | GEMINI_ADAPTER.READ_WRITE_AGENTS,
        )
        for name in GEMINI_ADAPTER.READ_ONLY_AGENTS:
            self.assertTrue(GEMINI_ADAPTER.is_read_only_agent(name))
        for name in GEMINI_ADAPTER.READ_WRITE_AGENTS:
            self.assertFalse(GEMINI_ADAPTER.is_read_only_agent(name))
        with self.assertRaises(ValueError):
            GEMINI_ADAPTER.is_read_only_agent("unknown-agent")

    def test_broken_symlinks_are_detected_and_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "tree"
            nested = root / "empty"
            nested.mkdir(parents=True)
            valid_file = root / "valid.md"
            valid_file.write_bytes(b"ok\n")
            broken_link = nested / "broken.md"
            broken_link.symlink_to(Path(temporary) / "does-not-exist")

            problems = GEMINI_ADAPTER.check_tree({valid_file: b"ok\n"}, root, "agent")
            self.assertEqual(1, len(problems))
            self.assertIn("unexpected symlink agent", problems[0])

            GEMINI_ADAPTER.remove_unexpected(root, {valid_file})
            self.assertFalse(broken_link.is_symlink())
            self.assertFalse(nested.exists())
            self.assertEqual(b"ok\n", valid_file.read_bytes())

    def test_atomic_write_replaces_broken_symlink_and_leaves_no_temp_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.md"
            target.symlink_to(root / "missing-target")

            GEMINI_ADAPTER.atomic_write(target, b"updated content\n")
            self.assertFalse(target.is_symlink())
            self.assertTrue(target.is_file())
            self.assertEqual(b"updated content\n", target.read_bytes())
            self.assertEqual([target], list(root.iterdir()))


if __name__ == "__main__":
    unittest.main()
