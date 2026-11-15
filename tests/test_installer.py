from __future__ import annotations

import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib
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
CLAUDE_ADAPTER = _load_script_module("claude_adapter", ROOT / "scripts" / "claude_adapter.py")
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
            self.assertFalse((root / ".gemini" / "policies").exists())

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
            self.assertIn(
                "`.gemini/policies/forgeos.toml` (also installed only with `--include-settings`)",
                gemini_entry,
            )
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
                home = home.resolve()
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
            self.assertTrue((target / ".gemini" / "policies" / "forgeos.toml").is_file())
            self.assertEqual(0, self.run_cli("uninstall", *common)[0])
            self.assertFalse((target / ".gemini" / "policies" / "forgeos.toml").exists())

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


def _extract_frontmatter_tools(markdown_text: str) -> list[str]:
    frontmatter = markdown_text.split("\n---\n", 1)[0]
    tools: list[str] = []
    in_tools = False
    for line in frontmatter.splitlines():
        if line.strip() == "tools:":
            in_tools = True
            continue
        if in_tools:
            if line.startswith("  - "):
                tools.append(line[4:].strip())
            elif line and not line.startswith(" "):
                break
    return tools


def _find_gemini_bundle_modules() -> tuple[Path, Path] | None:
    gemini_bin = shutil.which("gemini")
    if not gemini_bin:
        return None
    resolved = Path(gemini_bin).resolve()
    candidate_dirs = [resolved.parent]
    for parent in resolved.parents:
        candidate_dirs.append(
            parent / "lib" / "node_modules" / "@google" / "gemini-cli" / "bundle"
        )
        candidate_dirs.append(
            parent / "node_modules" / "@google" / "gemini-cli" / "bundle"
        )
    bundle_dir = next((d for d in candidate_dirs if d.is_dir()), None)
    if bundle_dir is None:
        return None
    settings_mod: Path | None = None
    core_mod: Path | None = None
    for js_file in sorted(bundle_dir.glob("*.js")):
        text = js_file.read_text(encoding="utf-8", errors="ignore")
        tail = text[text.rfind("export {"):] if "export {" in text else ""
        if not tail:
            continue
        if settings_mod is None and re.search(r"\bloadSettings\b", tail):
            settings_mod = js_file
        if (
            core_mod is None
            and re.search(r"\bcreatePolicyEngineConfig\b", tail)
            and re.search(r"\bPolicyEngine\b", tail)
            and re.search(r"\bgetEnvironmentMemoryPaths\b", tail)
        ):
            core_mod = js_file
        if settings_mod is not None and core_mod is not None:
            return settings_mod, core_mod
    return None


GEMINI_BUNDLE_MODULES = _find_gemini_bundle_modules()


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

    def test_antigravity_agent_tool_lists_match_native_tool_names(self) -> None:
        reviewer = (
            ROOT / ".gemini" / "antigravity-agents" / "code-reviewer.md"
        ).read_text(encoding="utf-8")
        backend = (
            ROOT / ".gemini" / "antigravity-agents" / "backend-engineer.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            ["view_file", "run_command", "manage_task", "search_web"],
            _extract_frontmatter_tools(reviewer),
        )
        self.assertEqual(
            [
                "view_file",
                "replace_file_content",
                "write_to_file",
                "run_command",
                "manage_task",
                "search_web",
            ],
            _extract_frontmatter_tools(backend),
        )

    def test_synchronize_rejects_symlinked_roots_without_modifying_external_target(self) -> None:
        cases = (
            ("claude-agents", CLAUDE_ADAPTER, (".claude", "agents"), True),
            ("claude-skills", CLAUDE_ADAPTER, (".claude", "skills"), True),
            ("claude-parent", CLAUDE_ADAPTER, (".claude",), True),
            ("gemini-agents", GEMINI_ADAPTER, (".gemini", "agents"), True),
            ("antigravity-agents", GEMINI_ADAPTER, (".gemini", "antigravity-agents"), True),
            ("gemini-skills", GEMINI_ADAPTER, (".gemini", "skills"), True),
            ("gemini-parent", GEMINI_ADAPTER, (".gemini",), True),
            ("agents-parent", GEMINI_ADAPTER, (".agents",), True),
            ("agents-manifest", GEMINI_ADAPTER, (".agents", "agents.json"), False),
        )
        for label, adapter, link_parts, is_dir in cases:
            with self.subTest(target=label), tempfile.TemporaryDirectory() as temporary:
                temp_root = Path(temporary) / "repo"
                temp_root.mkdir()
                external = Path(temporary) / "external"
                external.mkdir()
                sentinel = external / "sentinel.txt"
                sentinel.write_text("keep-external-data\n", encoding="utf-8")
                symlink_path = temp_root.joinpath(*link_parts)
                symlink_path.parent.mkdir(parents=True, exist_ok=True)
                if is_dir:
                    symlink_path.symlink_to(external, target_is_directory=True)
                else:
                    external_file = external / "target.json"
                    external_file.write_text('{"keep":true}\n', encoding="utf-8")
                    symlink_path.symlink_to(external_file, target_is_directory=False)

                if adapter is CLAUDE_ADAPTER:
                    patches = {
                        "ROOT": temp_root,
                        "CLAUDE_AGENTS": temp_root / ".claude" / "agents",
                        "CLAUDE_SKILLS": temp_root / ".claude" / "skills",
                    }
                    siblings = (
                        temp_root / ".claude" / "agents",
                        temp_root / ".claude" / "skills",
                    )
                else:
                    patches = {
                        "ROOT": temp_root,
                        "GEMINI_AGENTS": temp_root / ".gemini" / "agents",
                        "ANTIGRAVITY_AGENTS": temp_root / ".gemini" / "antigravity-agents",
                        "GEMINI_SKILLS": temp_root / ".gemini" / "skills",
                        "AGENTS_MANIFEST": temp_root / ".agents" / "agents.json",
                    }
                    siblings = (
                        temp_root / ".gemini" / "agents",
                        temp_root / ".gemini" / "antigravity-agents",
                        temp_root / ".gemini" / "skills",
                        temp_root / ".agents" / "agents.json",
                    )

                with mock.patch.multiple(adapter, **patches):
                    with self.assertRaises(ValueError):
                        adapter.synchronize()

                expected_external = (
                    {sentinel} if is_dir else {sentinel, external / "target.json"}
                )
                self.assertEqual(expected_external, set(external.iterdir()))
                self.assertEqual("keep-external-data\n", sentinel.read_text(encoding="utf-8"))
                if not is_dir:
                    self.assertEqual(
                        '{"keep":true}\n',
                        (external / "target.json").read_text(encoding="utf-8"),
                    )
                for sibling in siblings:
                    if not sibling.is_symlink():
                        self.assertFalse(sibling.exists())

    def test_synchronize_rejects_directory_at_target_file_without_partial_writes(self) -> None:
        cases = (
            ("claude-agent-dir", CLAUDE_ADAPTER, (".claude", "agents", "backend-engineer.md")),
            ("gemini-agent-dir", GEMINI_ADAPTER, (".gemini", "agents", "backend-engineer.md")),
            ("agents-manifest-dir", GEMINI_ADAPTER, (".agents", "agents.json")),
        )
        for label, adapter, dir_parts in cases:
            with self.subTest(target=label), tempfile.TemporaryDirectory() as temporary:
                temp_root = Path(temporary) / "repo"
                temp_root.mkdir()
                blocking_dir = temp_root.joinpath(*dir_parts)
                blocking_dir.mkdir(parents=True, exist_ok=True)
                keep_file = blocking_dir / "keep.txt"
                keep_file.write_text("keep\n", encoding="utf-8")

                if adapter is CLAUDE_ADAPTER:
                    patches = {
                        "ROOT": temp_root,
                        "CLAUDE_AGENTS": temp_root / ".claude" / "agents",
                        "CLAUDE_SKILLS": temp_root / ".claude" / "skills",
                    }
                    siblings = (temp_root / ".claude" / "skills",)
                else:
                    patches = {
                        "ROOT": temp_root,
                        "GEMINI_AGENTS": temp_root / ".gemini" / "agents",
                        "ANTIGRAVITY_AGENTS": temp_root / ".gemini" / "antigravity-agents",
                        "GEMINI_SKILLS": temp_root / ".gemini" / "skills",
                        "AGENTS_MANIFEST": temp_root / ".agents" / "agents.json",
                    }
                    siblings = tuple(
                        candidate
                        for candidate in (
                            temp_root / ".gemini" / "agents",
                            temp_root / ".gemini" / "antigravity-agents",
                            temp_root / ".gemini" / "skills",
                            temp_root / ".agents" / "agents.json",
                        )
                        if candidate != blocking_dir and not blocking_dir.is_relative_to(candidate)
                    )

                with mock.patch.multiple(adapter, **patches):
                    with self.assertRaises(ValueError):
                        adapter.synchronize()

                self.assertEqual("keep\n", keep_file.read_text(encoding="utf-8"))
                for sibling in siblings:
                    self.assertFalse(sibling.exists())

    def test_gemini_settings_and_policies_use_native_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "home"
            home.mkdir()
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                code = INSTALLER.main(
                    [
                        "install",
                        "--tool",
                        "gemini",
                        "--scope",
                        "global",
                        "--home",
                        str(home),
                        "--include-settings",
                    ]
                )
            self.assertEqual(0, code)

            settings = json.loads(
                (home / ".gemini" / "settings.json").read_text(encoding="utf-8")
            )
            self.assertNotIn("permissions", settings)
            self.assertNotIn("contextFileName", settings)
            self.assertEqual(
                ["AGENTS.md", "GEMINI.md", ".gemini/GEMINI.md"],
                settings["context"]["fileName"],
            )
            self.assertEqual("default", settings["general"]["defaultApprovalMode"])
            self.assertEqual([".gemini/policies", "~/.gemini/policies"], settings["policyPaths"])

            policy_doc = tomllib.loads(
                (home / ".gemini" / "policies" / "forgeos.toml").read_text(encoding="utf-8")
            )
            rules = policy_doc["rule"]
            ask_prefixes = {
                prefix
                for rule in rules
                if rule.get("toolName") == "run_shell_command"
                and rule.get("decision") == "ask_user"
                for prefix in rule.get("commandPrefix", [])
            }
            self.assertEqual(
                {
                    "git push",
                    "git merge",
                    "git tag",
                    "gh release",
                    "docker push",
                    "npm publish",
                    "eas update",
                    "eas submit",
                    "terraform apply",
                    "terraform destroy",
                    "kubectl apply",
                    "kubectl delete",
                },
                ask_prefixes,
            )

    @unittest.skipUnless(
        GEMINI_BUNDLE_MODULES is not None and shutil.which("node") is not None,
        "Gemini CLI / Node.js runtime unavailable",
    )
    def test_gemini_cli_loads_settings_and_enforces_policies_in_isolated_home(self) -> None:
        assert GEMINI_BUNDLE_MODULES is not None
        settings_mod, core_mod = GEMINI_BUNDLE_MODULES
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "home"
            home.mkdir()
            home = home.resolve()
            workspace = Path(temporary) / "workspace"
            workspace.mkdir()
            workspace = workspace.resolve()

            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                self.assertEqual(
                    0,
                    INSTALLER.main(
                        [
                            "install",
                            "--tool",
                            "gemini",
                            "--scope",
                            "global",
                            "--home",
                            str(home),
                            "--include-settings",
                        ]
                    ),
                )
                self.assertEqual(
                    0,
                    INSTALLER.main(
                        [
                            "install",
                            "--tool",
                            "gemini",
                            "--scope",
                            "local",
                            "--target",
                            str(workspace),
                            "--include-settings",
                        ]
                    ),
                )

            (home / ".gemini" / "trustedFolders.json").write_text(
                json.dumps({str(workspace): "TRUST_FOLDER"}),
                encoding="utf-8",
            )
            env = {
                **os.environ,
                "HOME": str(home),
                "USERPROFILE": str(home),
                "GEMINI_CLI_HOME": str(home),
            }
            node_script = """
import path from "node:path";
import os from "node:os";
import { pathToFileURL } from "node:url";

const [settingsModPath, coreModPath, workspaceDir] = process.argv.slice(1);
const { loadSettings } = await import(pathToFileURL(settingsModPath).href);
const {
  createPolicyEngineConfig,
  PolicyEngine,
  getEnvironmentMemoryPaths,
  getGlobalMemoryPaths,
  setGeminiMdFilename,
} = await import(pathToFileURL(coreModPath).href);

const loaded = loadSettings(workspaceDir);
if (loaded.merged.context?.fileName) {
  setGeminiMdFilename(loaded.merged.context.fileName);
}
const globalMemory = await getGlobalMemoryPaths();
const envMemory = await getEnvironmentMemoryPaths([workspaceDir]);

const resolvePath = (p) => {
  if (p === "~") return os.homedir();
  if (p.startsWith("~/")) return path.join(os.homedir(), p.slice(2));
  return path.resolve(workspaceDir, p);
};
const resolvedPolicyPaths = (loaded.merged.policyPaths || []).map(resolvePath);
const mode = loaded.merged.general?.defaultApprovalMode || "default";
const policyCfg = await createPolicyEngineConfig(
  { policyPaths: resolvedPolicyPaths },
  mode,
  undefined,
  true
);
const engine = new PolicyEngine({
  rules: policyCfg.rules,
  checkers: policyCfg.checkers,
  defaultDecision: policyCfg.defaultDecision,
  approvalMode: mode,
});

const checks = {};
for (const [label, name, args] of [
  ["read_env", "read_file", { file_path: ".env" }],
  ["read_env_prod", "read_file", { file_path: "sub/.env.production" }],
  ["write_env", "write_file", { file_path: ".env", content: "SECRET=1" }],
  ["replace_env_local", "replace", { file_path: ".env.local", old_string: "a", new_string: "b" }],
  ["read_env_example", "read_file", { file_path: ".env.example" }],
  ["read_env_sample", "read_file", { file_path: ".env.sample" }],
  ["read_env_template", "read_file", { file_path: ".env.template" }],
  ["read_envrc", "read_file", { file_path: ".envrc" }],
  ["many_env", "read_many_files", { include: [".env"] }],
  ["many_env_glob", "read_many_files", { include: [".env*"] }],
  ["many_env_deep_glob", "read_many_files", { include: ["**/.env*"] }],
  ["many_mixed_glob", "read_many_files", { include: [".env.example", ".env*"] }],
  ["many_exclude_env", "read_many_files", { include: ["src/**"], exclude: [".env"] }],
  ["many_example", "read_many_files", { include: [".env.example"] }],
  ["many_mixed", "read_many_files", { include: [".env.example", ".env"] }],
  ["shell_git_push", "run_shell_command", { command: "git push origin main" }],
  ["shell_terraform_apply", "run_shell_command", { command: "terraform apply" }],
  ["shell_docker_push", "run_shell_command", { command: "docker push org/app:latest" }],
  ["shell_git_status", "run_shell_command", { command: "git status" }],
]) {
  checks[label] = (await engine.check({ name, args })).decision;
}

console.log(
  "RESULT_JSON:" +
    JSON.stringify({
      errors: loaded.errors,
      contextFileName: loaded.merged.context?.fileName,
      defaultApprovalMode: loaded.merged.general?.defaultApprovalMode,
      globalMemory,
      envMemory,
      checks,
    })
);
"""
            proc = subprocess.run(
                [
                    "node",
                    "--input-type=module",
                    "-e",
                    node_script,
                    str(settings_mod),
                    str(core_mod),
                    str(workspace),
                ],
                env=env,
                cwd=workspace,
                capture_output=True,
                text=True,
                check=True,
            )
            payload_line = next(
                line for line in proc.stdout.splitlines() if line.startswith("RESULT_JSON:")
            )
            result = json.loads(payload_line.removeprefix("RESULT_JSON:"))

            # 1. Context-file loading
            self.assertEqual([], result["errors"])
            self.assertEqual(
                ["AGENTS.md", "GEMINI.md", ".gemini/GEMINI.md"],
                result["contextFileName"],
            )
            self.assertEqual(
                [str(home / ".gemini" / "GEMINI.md")],
                result["globalMemory"],
            )
            self.assertEqual(
                sorted(
                    [
                        str(workspace / "AGENTS.md"),
                        str(workspace / ".gemini" / "GEMINI.md"),
                    ]
                ),
                sorted(result["envMemory"]),
            )

            # 2. Default approval mode
            self.assertEqual("default", result["defaultApprovalMode"])

            # 3. Sensitive-file access restrictions
            checks = result["checks"]
            for denied_key in (
                "read_env",
                "read_env_prod",
                "write_env",
                "replace_env_local",
                "many_env",
                "many_env_glob",
                "many_env_deep_glob",
                "many_mixed_glob",
                "many_mixed",
            ):
                self.assertEqual("deny", checks[denied_key], f"Expected deny for {denied_key}")
            self.assertEqual("ask_user", checks["many_exclude_env"])
            for allowed_key in (
                "read_env_example",
                "read_env_sample",
                "read_env_template",
                "read_envrc",
                "many_example",
            ):
                self.assertEqual("allow", checks[allowed_key], f"Expected allow for {allowed_key}")

            # 4. Confirmation behavior for controlled commands
            for ask_key in ("shell_git_push", "shell_terraform_apply", "shell_docker_push"):
                self.assertEqual("ask_user", checks[ask_key], f"Expected ask_user for {ask_key}")
            self.assertEqual("allow", checks["shell_git_status"])

    def test_broken_symlinks_are_detected_and_removed(self) -> None:
        for label, adapter in (("claude", CLAUDE_ADAPTER), ("gemini", GEMINI_ADAPTER)):
            with self.subTest(adapter=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "tree"
                nested = root / "empty"
                nested.mkdir(parents=True)
                valid_file = root / "valid.md"
                valid_file.write_bytes(b"ok\n")
                broken_link = nested / "broken.md"
                broken_link.symlink_to(Path(temporary) / "does-not-exist")

                problems = adapter.check_tree({valid_file: b"ok\n"}, root, "agent")
                self.assertEqual(1, len(problems))
                self.assertIn("unexpected symlink agent", problems[0])

                adapter.remove_unexpected(root, {valid_file})
                self.assertFalse(broken_link.is_symlink())
                self.assertFalse(nested.exists())
                self.assertEqual(b"ok\n", valid_file.read_bytes())

    def test_atomic_write_replaces_broken_symlink_and_leaves_no_temp_files(self) -> None:
        for label, adapter in (("claude", CLAUDE_ADAPTER), ("gemini", GEMINI_ADAPTER)):
            with self.subTest(adapter=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                target = root / "target.md"
                target.symlink_to(root / "missing-target")

                adapter.atomic_write(target, b"updated content\n")
                self.assertFalse(target.is_symlink())
                self.assertTrue(target.is_file())
                self.assertEqual(b"updated content\n", target.read_bytes())
                self.assertEqual([target], list(root.iterdir()))


if __name__ == "__main__":
    unittest.main()
