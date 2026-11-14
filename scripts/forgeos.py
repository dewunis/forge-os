#!/usr/bin/env python3
"""Install, update, inspect, or uninstall ForgeOS without external dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import sys
import tempfile
from typing import Iterable


SOURCE_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_VERSION = 1
MANIFEST_NAME = "install-manifest.json"
TOOLS = {"codex", "claude", "all"}


class InstallError(RuntimeError):
    """A safe, user-facing installation error."""


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def selected_tools(value: str) -> tuple[str, ...]:
    if value == "all":
        return ("codex", "claude")
    return (value,)


def files_below(root: Path) -> Iterable[Path]:
    if not root.exists():
        return ()
    return sorted(path for path in root.rglob("*") if path.is_file())


def add_tree(plan: dict[Path, bytes], source: Path, destination: Path) -> None:
    for path in files_below(source):
        plan[destination / path.relative_to(source)] = path.read_bytes()


def replace_text(content: bytes, replacements: dict[str, str]) -> bytes:
    text = content.decode("utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("utf-8")


def roots(args: argparse.Namespace) -> tuple[Path, Path]:
    if args.scope == "global":
        if args.target:
            raise InstallError("--target is valid only with --scope local")
        base = Path(args.home).expanduser() if args.home else Path.home()
    else:
        if args.home:
            raise InstallError("--home is valid only with --scope global")
        base = Path(args.target).expanduser() if args.target else Path.cwd()
    base = base.resolve()
    shared = base / ".forgeos"
    return base, shared


def manifest_path(base: Path) -> Path:
    return base / ".forgeos" / MANIFEST_NAME


def safe_destination(base: Path, relative: str) -> Path:
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise InstallError(f"unsafe relative path in installation manifest: {relative}")
    candidate = base / relative_path
    resolved_base = base.resolve()
    resolved = candidate.resolve(strict=False)
    if resolved != resolved_base and resolved_base not in resolved.parents:
        raise InstallError(f"unsafe path outside installation root: {relative}")
    return candidate


def relative_name(base: Path, path: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError as exc:
        raise InstallError(f"path is outside installation root: {path}") from exc


def safe_backup_destination(base: Path, relative: str) -> Path:
    if not relative.startswith(".forgeos/backups/"):
        raise InstallError(f"invalid ForgeOS backup path: {relative}")
    candidate = safe_destination(base, relative)
    backup_root = (base / ".forgeos" / "backups").resolve(strict=False)
    resolved = candidate.resolve(strict=False)
    if resolved != backup_root and backup_root not in resolved.parents:
        raise InstallError(f"backup path escapes ForgeOS backup storage: {relative}")
    if candidate.is_symlink():
        raise InstallError(f"ForgeOS backup path must not be a symlink: {relative}")
    return candidate


def render_governance(
    content: bytes,
    base: Path,
    shared: Path,
    tools: tuple[str, ...],
    scope: str,
) -> bytes:
    if scope == "local":
        agent_reference = (
            ".forgeos/sources/agents/*.toml"
            if "claude" in tools and "codex" not in tools
            else ".codex/agents/*.toml"
        )
        skill_reference = (
            ".claude/skills/*/SKILL.md"
            if "claude" in tools and "codex" not in tools
            else ".agents/skills/*/SKILL.md"
        )
        documentation_root = "docs"
        standards_root = "standards"
        profiles_root = "profiles/"
    elif "claude" in tools and "codex" not in tools:
        agent_reference = f"{shared.as_posix()}/sources/agents/*.toml"
        skill_reference = f"{base.as_posix()}/.claude/skills/*/SKILL.md"
        documentation_root = f"{shared.as_posix()}/docs"
        standards_root = f"{shared.as_posix()}/standards"
        profiles_root = f"{shared.as_posix()}/profiles/"
    else:
        agent_reference = f"{base.as_posix()}/.codex/agents/*.toml"
        skill_reference = f"{base.as_posix()}/.agents/skills/*/SKILL.md"
        documentation_root = f"{shared.as_posix()}/docs"
        standards_root = f"{shared.as_posix()}/standards"
        profiles_root = f"{shared.as_posix()}/profiles/"
    return replace_text(
        content,
        {
            ".codex/agents/*.toml": agent_reference,
            ".agents/skills/*/SKILL.md": skill_reference,
            "docs/architecture.md": f"{documentation_root}/architecture.md",
            "docs/permissions.md": f"{documentation_root}/permissions.md",
            "standards/naming-conventions.md": f"{standards_root}/naming-conventions.md",
            "profiles/": profiles_root,
            (
                "Do not edit generated Claude agent or Skill files directly; run "
                "`python scripts/claude_adapter.py` and then `python "
                "scripts/claude_adapter.py --check` after changing a canonical source."
            ): (
                "Do not edit installed Claude agent or Skill files directly. "
                "Update them from a validated ForgeOS source checkout with the "
                "ForgeOS installer."
            ),
        },
    )


def render_claude_entry(
    content: bytes,
    *,
    scope: str,
    claude_only: bool,
    source_agent_root: Path,
    skill_root: Path,
) -> bytes:
    replacements = {
        (
            "- Do not edit generated agent or Skill files directly. Update the "
            "canonical source, run `python scripts/claude_adapter.py`, then run "
            "`python scripts/claude_adapter.py --check`."
        ): (
            "- Do not edit installed agent or Skill files directly. Update them "
            "from a validated ForgeOS source checkout with the ForgeOS installer."
        ),
        "- Claude-specific settings are in `.claude/settings.json`.": (
            "- Claude-specific settings are in `.claude/settings.json` only when "
            "the installer was run with `--include-settings`."
        ),
    }
    if scope == "global":
        replacements["@../AGENTS.md"] = "@../.forgeos/AGENTS.md"
    if claude_only:
        replacements[
            "- `.codex/agents/*.toml` is the canonical source for the 17 specialist "
            "role definitions. `.claude/agents/*.md` is generated from it."
        ] = (
            f"- The installed role provenance is `{source_agent_root.as_posix()}/*.toml`; "
            "the ForgeOS repository remains the canonical source."
        )
        replacements[
            "- `.agents/skills/*/SKILL.md` is the canonical source for reusable "
            "procedures. `.claude/skills/` is a generated Claude Code mirror."
        ] = (
            f"- Installed Claude Skills are in `{skill_root.as_posix()}/*/SKILL.md`; "
            "the ForgeOS repository remains the canonical source."
        )
    return replace_text(content, replacements)


def build_plan(args: argparse.Namespace, base: Path, shared: Path) -> dict[Path, bytes]:
    tools = selected_tools(args.tool)
    plan: dict[Path, bytes] = {}

    resource_root = shared if args.scope == "global" else base
    governance = render_governance(
        (SOURCE_ROOT / "AGENTS.md").read_bytes(), base, shared, tools, args.scope
    )
    plan[resource_root / "AGENTS.md"] = governance
    add_tree(plan, SOURCE_ROOT / "docs", resource_root / "docs")
    add_tree(plan, SOURCE_ROOT / "profiles", resource_root / "profiles")
    add_tree(plan, SOURCE_ROOT / "standards", resource_root / "standards")
    canonical_skill_root = (
        base / ".claude" / "skills"
        if "claude" in tools and "codex" not in tools
        else base / ".agents" / "skills"
    )
    canonical_skill_prefix = (
        ".claude/skills/"
        if args.scope == "local" and "claude" in tools and "codex" not in tools
        else ".agents/skills/"
        if args.scope == "local"
        else f"{canonical_skill_root.as_posix()}/"
    )
    for source in files_below(SOURCE_ROOT / ".codex" / "agents"):
        plan[shared / "sources" / "agents" / source.name] = replace_text(
            source.read_bytes(), {".agents/skills/": canonical_skill_prefix}
        )

    if "codex" in tools:
        codex_root = base / ".codex"
        if args.scope == "global":
            plan[codex_root / "AGENTS.md"] = governance
        skill_root = base / ".agents" / "skills"
        skill_prefix = (
            ".agents/skills/"
            if args.scope == "local"
            else f"{skill_root.as_posix()}/"
        )
        for source in files_below(SOURCE_ROOT / ".codex" / "agents"):
            content = replace_text(
                source.read_bytes(), {".agents/skills/": skill_prefix}
            )
            plan[codex_root / "agents" / source.name] = content
        add_tree(plan, SOURCE_ROOT / ".agents" / "skills", skill_root)
        if args.include_settings:
            plan[codex_root / "config.toml"] = (
                SOURCE_ROOT / ".codex" / "config.toml"
            ).read_bytes()

    if "claude" in tools:
        claude_root = base / ".claude"
        skill_root = claude_root / "skills"
        source_agent_root = shared / "sources" / "agents"
        claude_entry = render_claude_entry(
            (SOURCE_ROOT / ".claude" / "CLAUDE.md").read_bytes(),
            scope=args.scope,
            claude_only="codex" not in tools,
            source_agent_root=source_agent_root,
            skill_root=skill_root,
        )
        plan[claude_root / "CLAUDE.md"] = claude_entry
        rendered_skill_root = (
            ".claude/skills" if args.scope == "local" else skill_root.as_posix()
        )
        rendered_source_agent_root = (
            ".forgeos/sources/agents"
            if args.scope == "local"
            else source_agent_root.as_posix()
        )
        for source in files_below(SOURCE_ROOT / ".claude" / "agents"):
            content = replace_text(
                source.read_bytes(),
                {
                    ".agents/skills/": f"{rendered_skill_root}/",
                    "Canonical role source: `.codex/agents/": (
                        f"Canonical role source: `{rendered_source_agent_root}/"
                    ),
                },
            )
            plan[claude_root / "agents" / source.name] = content
        add_tree(plan, SOURCE_ROOT / ".agents" / "skills", skill_root)
        if args.include_settings:
            plan[claude_root / "settings.json"] = (
                SOURCE_ROOT / ".claude" / "settings.json"
            ).read_bytes()

    return plan


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def read_manifest(base: Path) -> dict[str, object]:
    path = manifest_path(base)
    if not path.is_file():
        raise InstallError(f"ForgeOS is not installed at {base}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallError(f"invalid ForgeOS manifest: {path}") from exc
    if data.get("manifest_version") != MANIFEST_VERSION or not isinstance(
        data.get("files"), dict
    ):
        raise InstallError(f"unsupported ForgeOS manifest: {path}")
    if data.get("scope") not in {"global", "local"}:
        raise InstallError(f"invalid ForgeOS manifest scope: {path}")
    tools = data.get("tools")
    if not isinstance(tools, list) or not tools or any(
        tool not in {"codex", "claude"} for tool in tools
    ):
        raise InstallError(f"invalid ForgeOS manifest tools: {path}")
    for relative, entry in data["files"].items():
        if not isinstance(relative, str) or not relative or not isinstance(entry, dict):
            raise InstallError(f"invalid ForgeOS manifest file entry: {path}")
        safe_destination(base, relative)
        digest = entry.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise InstallError(f"invalid ForgeOS manifest digest: {relative}")
        backup = entry.get("backup")
        if backup is not None:
            if not isinstance(backup, str):
                raise InstallError(f"invalid ForgeOS backup path: {relative}")
            safe_backup_destination(base, backup)
    snapshots = data.get("update_snapshots", [])
    if not isinstance(snapshots, list):
        raise InstallError(f"invalid ForgeOS update snapshots: {path}")
    for snapshot in snapshots:
        if not isinstance(snapshot, str):
            raise InstallError(f"invalid ForgeOS update snapshot: {path}")
        safe_backup_destination(base, snapshot)
    return data


def backup_path(base: Path, relative: str, backup_id: str) -> Path:
    return base / ".forgeos" / "backups" / backup_id / Path(relative)


def install(args: argparse.Namespace) -> int:
    base, shared = roots(args)
    existing_manifest = manifest_path(base)
    if existing_manifest.exists():
        raise InstallError(
            f"ForgeOS already has an ownership manifest at {existing_manifest}; use update"
        )
    plan = build_plan(args, base, shared)
    conflicts: list[Path] = []
    for path in plan:
        safe_destination(base, relative_name(base, path))
        if path.exists() or path.is_symlink():
            conflicts.append(path)
    if conflicts and args.conflict == "fail":
        listed = "\n  ".join(str(path) for path in conflicts[:10])
        raise InstallError(f"existing files would be replaced:\n  {listed}")

    backup_id = f"{os.getpid()}-{secrets.token_hex(6)}"
    backups: dict[Path, Path] = {}
    written: list[Path] = []
    try:
        for path in conflicts:
            if not path.is_file() or path.is_symlink():
                raise InstallError(f"cannot back up non-regular file: {path}")
            relative = relative_name(base, path)
            backup = backup_path(base, relative, backup_id)
            backup.parent.mkdir(parents=True, exist_ok=True)
            os.replace(path, backup)
            backups[path] = backup
        for path, content in plan.items():
            atomic_write(path, content)
            written.append(path)
        files = {}
        for path, content in sorted(plan.items(), key=lambda item: str(item[0])):
            relative = relative_name(base, path)
            entry: dict[str, str] = {"sha256": sha256(content)}
            if path in backups:
                entry["backup"] = relative_name(base, backups[path])
            files[relative] = entry
        manifest = {
            "manifest_version": MANIFEST_VERSION,
            "scope": args.scope,
            "tools": list(selected_tools(args.tool)),
            "include_settings": bool(args.include_settings),
            "files": files,
        }
        atomic_write(
            existing_manifest,
            (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
    except BaseException:
        for path in reversed(written):
            path.unlink(missing_ok=True)
        for path, backup in backups.items():
            if backup.exists() and not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                os.replace(backup, path)
        raise
    print(f"Installed ForgeOS ({args.tool}, {args.scope}): {len(plan)} files at {base}")
    return 0


def validate_request(
    args: argparse.Namespace,
    manifest: dict[str, object],
    *,
    check_settings: bool = False,
) -> None:
    expected = list(selected_tools(args.tool))
    if manifest.get("scope") != args.scope:
        raise InstallError("requested scope does not match the installed manifest")
    if manifest.get("tools") != expected:
        raise InstallError(
            "requested tool selection does not match the installed manifest: "
            + ", ".join(manifest.get("tools", []))
        )
    if check_settings and bool(manifest.get("include_settings")) != bool(
        args.include_settings
    ):
        raise InstallError(
            "--include-settings must match the installed manifest during update"
        )


def update(args: argparse.Namespace) -> int:
    base, shared = roots(args)
    manifest = read_manifest(base)
    validate_request(args, manifest, check_settings=True)
    plan = build_plan(args, base, shared)
    old_files = manifest["files"]
    assert isinstance(old_files, dict)

    drift: list[Path] = []
    collisions: list[Path] = []
    for relative, entry in old_files.items():
        path = safe_destination(base, relative)
        installed_hash = entry.get("sha256") if isinstance(entry, dict) else None
        if (
            not path.is_file()
            or path.is_symlink()
            or sha256(path.read_bytes()) != installed_hash
        ):
            drift.append(path)
    for path in plan:
        relative = relative_name(base, path)
        if relative not in old_files and (path.exists() or path.is_symlink()):
            collisions.append(path)
    blockers = drift + collisions
    if blockers and args.conflict == "fail":
        listed = "\n  ".join(str(path) for path in blockers[:10])
        raise InstallError(f"update refused because of drift or conflicts:\n  {listed}")

    planned_relatives = {relative_name(base, path) for path in plan}
    obsolete = set(old_files) - planned_relatives
    obsolete_backups: dict[Path, Path] = {}
    changed: dict[Path, bytes | None] = {}
    for relative in obsolete:
        path = safe_destination(base, relative)
        changed[path] = None
        previous = old_files[relative]
        backup_name = previous.get("backup") if isinstance(previous, dict) else None
        if backup_name:
            backup = safe_backup_destination(base, backup_name)
            if not backup.is_file() or backup.is_symlink():
                raise InstallError(
                    f"pre-installation backup for obsolete file is unavailable: {backup}"
                )
            obsolete_backups[path] = backup
    for path, content in plan.items():
        safe_destination(base, relative_name(base, path))
        if not path.is_file() or path.read_bytes() != content:
            changed[path] = content

    for path in changed:
        safe_destination(base, relative_name(base, path))
        if (path.exists() or path.is_symlink()) and (
            not path.is_file() or path.is_symlink()
        ):
            raise InstallError(f"cannot update non-regular file: {path}")

    backup_id = f"update-{os.getpid()}-{secrets.token_hex(6)}"
    recovery: dict[Path, Path | None] = {}
    snapshot_names: list[str] = []
    original_manifest = json.loads(json.dumps(manifest))
    try:
        # Snapshot every existing file that will change before the first mutation.
        for path in changed:
            if path.is_file():
                relative = relative_name(base, path)
                snapshot = backup_path(base, relative, backup_id)
                snapshot.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, snapshot)
                recovery[path] = snapshot
                snapshot_names.append(relative_name(base, snapshot))
            else:
                recovery[path] = None

        for path, content in changed.items():
            if content is None:
                original = obsolete_backups.get(path)
                if original:
                    atomic_write(path, original.read_bytes())
                else:
                    path.unlink(missing_ok=True)
                    prune_empty(path.parent, base)
            else:
                atomic_write(path, content)

        new_entries: dict[str, dict[str, str]] = {}
        for path, content in plan.items():
            relative = relative_name(base, path)
            previous = old_files.get(relative)
            entry = {"sha256": sha256(content)}
            # Preserve a pre-installation backup. An update snapshot is only the
            # uninstall backup when this update newly takes ownership of a conflict.
            backup_value = previous.get("backup") if isinstance(previous, dict) else None
            if backup_value:
                entry["backup"] = backup_value
            elif relative not in old_files and recovery.get(path) is not None:
                entry["backup"] = relative_name(base, recovery[path])
            new_entries[relative] = entry
        manifest["files"] = new_entries
        historical_snapshots = manifest.get("update_snapshots", [])
        if not isinstance(historical_snapshots, list):
            historical_snapshots = []
        uninstall_backups = {
            entry.get("backup")
            for entry in new_entries.values()
            if isinstance(entry, dict) and entry.get("backup")
        }
        manifest["update_snapshots"] = historical_snapshots + [
            name for name in snapshot_names if name not in uninstall_backups
        ] + [relative_name(base, path) for path in obsolete_backups.values()]
        atomic_write(
            manifest_path(base),
            (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
    except BaseException:
        for path, snapshot in reversed(list(recovery.items())):
            if snapshot and snapshot.is_file():
                atomic_write(path, snapshot.read_bytes())
            else:
                path.unlink(missing_ok=True)
        for snapshot in recovery.values():
            if snapshot:
                snapshot.unlink(missing_ok=True)
                prune_empty(snapshot.parent, base / ".forgeos" / "backups")
        # The manifest replacement is atomic, but restore it as well if an
        # exception is raised after replacement by a future extension.
        atomic_write(
            manifest_path(base),
            (json.dumps(original_manifest, indent=2, sort_keys=True) + "\n").encode(
                "utf-8"
            ),
        )
        raise
    print(f"Updated ForgeOS ({args.tool}, {args.scope}): {len(plan)} files at {base}")
    return 0


def status(args: argparse.Namespace) -> int:
    base, _ = roots(args)
    if not manifest_path(base).is_file():
        print(f"ForgeOS status: ABSENT at {base}")
        return 0
    manifest = read_manifest(base)
    validate_request(args, manifest)
    problems: list[str] = []
    for relative, entry in manifest["files"].items():
        path = safe_destination(base, relative)
        if not path.is_file() or path.is_symlink():
            problems.append(f"missing: {relative}")
        elif sha256(path.read_bytes()) != entry.get("sha256"):
            problems.append(f"modified: {relative}")
    if problems:
        for problem in problems:
            print(f"DRIFT: {problem}")
        print(f"ForgeOS status: drift detected ({len(problems)} files)")
        return 1
    print(
        f"ForgeOS status: healthy ({len(manifest['files'])} owned files, "
        f"{', '.join(manifest['tools'])})"
    )
    return 0


def prune_empty(path: Path, stop: Path) -> None:
    current = path
    while current != stop and current.exists():
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def uninstall(args: argparse.Namespace) -> int:
    base, _ = roots(args)
    manifest = read_manifest(base)
    validate_request(args, manifest)
    remaining: dict[str, object] = {}
    restored = 0
    removed = 0
    for relative, entry in sorted(manifest["files"].items(), reverse=True):
        path = safe_destination(base, relative)
        expected = entry.get("sha256")
        backup_name = entry.get("backup")
        backup = safe_backup_destination(base, backup_name) if backup_name else None
        if (path.exists() or path.is_symlink()) and (
            not path.is_file()
            or path.is_symlink()
            or sha256(path.read_bytes()) != expected
        ):
            print(f"PRESERVED: modified owned file {path}")
            remaining[relative] = entry
            continue
        path.unlink(missing_ok=True)
        removed += 1
        if backup and backup.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(backup, path)
            restored += 1
            prune_empty(backup.parent, base / ".forgeos" / "backups")
        else:
            prune_empty(path.parent, base)
    if remaining:
        manifest["files"] = remaining
        atomic_write(
            manifest_path(base),
            (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
        print(f"Uninstall incomplete: {len(remaining)} modified files remain owned")
        return 1
    snapshots = manifest.get("update_snapshots", [])
    manifest_path(base).unlink(missing_ok=True)
    prune_empty(base / ".forgeos" / "backups", base)
    prune_empty(base / ".forgeos", base)
    if snapshots:
        print(
            f"PRESERVED: {len(snapshots)} update recovery snapshots remain under "
            f"{base / '.forgeos' / 'backups'}"
        )
    print(
        f"Uninstalled ForgeOS: {removed} files removed, {restored} backups restored, "
        f"{len(snapshots)} recovery snapshots preserved"
    )
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="command", required=True)
    for command in ("install", "update", "uninstall", "status"):
        child = subparsers.add_parser(command)
        child.add_argument("--tool", choices=sorted(TOOLS), default="all")
        child.add_argument("--scope", choices=("global", "local"), default="global")
        child.add_argument("--target", help="local project directory (default: current directory)")
        child.add_argument("--home", help="override the user home for global installation/testing")
        if command in {"install", "update"}:
            child.add_argument("--conflict", choices=("fail", "backup"), default="fail")
            child.add_argument("--include-settings", action="store_true")
        else:
            child.add_argument("--include-settings", action="store_true", help=argparse.SUPPRESS)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return {
            "install": install,
            "update": update,
            "uninstall": uninstall,
            "status": status,
        }[args.command](args)
    except InstallError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
