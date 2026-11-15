# Installation and maintenance

**English** | [Français](installation.fr.md)

## Prerequisites

- Python 3.9+ for `scripts/forgeos.py`. The installer uses only the Python standard library.
- Codex, Claude Code, Google Antigravity (`agy` CLI / Antigravity IDE), and/or Gemini CLI installed and authenticated separately per their official documentation.
- Python 3.11+ only for `scripts/bootstrap.py`, because the source validator parses TOML with `tomllib`.

The installer downloads no dependencies and modifies no remote services.

## Commands

```text
python scripts/forgeos.py install   [options]
python scripts/forgeos.py update    [options]
python scripts/forgeos.py status    [options]
python scripts/forgeos.py uninstall [options]
```

Common options:

- `--tool codex|claude|gemini|all`: adapter to manage (`gemini` targets Google Antigravity `agy` CLI / Antigravity IDE and Gemini CLI); default `all`.
- `--scope global|local`: user or project installation; default `global`.
- `--target PATH`: target project for a local installation; default current working directory.
- `--home PATH`: user home override for an isolated or managed global installation. Intended primarily for testing; never point it at a real profile accidentally.

Write options:

- `--conflict fail|backup` for `install` and `update`; default `fail`.
- `--include-settings`: explicit consent to install `.codex/config.toml`, `.claude/settings.json`, and/or `.gemini/settings.json` (plus `.gemini/policies/`).

Scope and tool selection used for `update`, `status`, and `uninstall` must match the installation manifest.

## Local installation

### Windows PowerShell

```powershell
python .\scripts\forgeos.py install --tool all --scope local --target C:\src\my-project
```

### macOS and Linux

```shell
python3 ./scripts/forgeos.py install --tool all --scope local --target /srv/my-project
```

A local installation places files in the project's native locations:

| Component | Codex | Claude Code | Antigravity / Gemini CLI |
| --- | --- | --- | --- |
| Governance | `AGENTS.md` | `AGENTS.md` imported by `.claude/CLAUDE.md` | `AGENTS.md` imported by `.gemini/GEMINI.md` |
| Agents | `.codex/agents/*.toml` | `.claude/agents/*.md` | `.gemini/agents/*.md` (Gemini CLI) and `.gemini/antigravity-agents/*.md` (Antigravity) |
| Antigravity discovery | — | — | `.agents/agents.json` -> `.gemini/antigravity-agents` (+ `.agents/skills.json` when `gemini`-only) |
| Skills | `.agents/skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` | `.gemini/skills/*/SKILL.md` |
| Resources | `docs/`, `profiles/`, `standards/` | `docs/`, `profiles/`, `standards/` | `docs/`, `profiles/`, `standards/` |
| Ownership | `.forgeos/install-manifest.json` | `.forgeos/install-manifest.json` | `.forgeos/install-manifest.json` |

A `claude`-only installation keeps its internal ForgeOS sources under `.forgeos/sources/` and does not create `.codex/` or `.agents/`. A `gemini`-only installation creates only the Antigravity discovery manifests `.agents/agents.json` and `.agents/skills.json` (without `.codex/` or `.agents/skills/`).

## Global installation

### Windows PowerShell

```powershell
python .\scripts\forgeos.py install --tool all --scope global
```

### macOS and Linux

```shell
python3 ./scripts/forgeos.py install --tool all --scope global
```

Python resolves the user's home directory without hardcoded paths. Destination paths inside that directory are identical across all three platforms:

| Component | Global destination |
| --- | --- |
| Codex governance | `~/.codex/AGENTS.md` |
| Codex agents | `~/.codex/agents/*.toml` |
| Codex Skills | `~/.agents/skills/*/SKILL.md` |
| Claude entrypoint | `~/.claude/CLAUDE.md` |
| Claude agents | `~/.claude/agents/*.md` |
| Claude Skills | `~/.claude/skills/*/SKILL.md` |
| Gemini entrypoint | `~/.gemini/GEMINI.md` |
| Antigravity governance | `~/.gemini/config/GEMINI.md` |
| Antigravity agent discovery | `~/.gemini/config/agents.json` (-> `~/.gemini/antigravity-agents`) |
| Antigravity Skill discovery | `~/.gemini/config/skills.json` (-> `~/.gemini/skills`) |
| Gemini CLI agents | `~/.gemini/agents/*.md` |
| Antigravity agents | `~/.gemini/antigravity-agents/*.md` |
| Gemini / Antigravity Skills | `~/.gemini/skills/*/SKILL.md` |
| Shared resources and manifest | `~/.forgeos/` |

Global Claude and Gemini entrypoints (as well as `~/.gemini/config/GEMINI.md`) import `~/.forgeos/AGENTS.md`. Skill references inside agents are rendered to target paths so they do not depend on the current working directory.

## Optional settings

By default, the installer does not copy `.codex/config.toml`, `.claude/settings.json`, or `.gemini/settings.json` (and `.gemini/policies/`). This avoids implicitly altering a user's sandboxing, approvals, reasoning level, or permissions.

To include them after inspection:

```shell
python3 scripts/forgeos.py install --tool all --scope global --include-settings
```

This option must also be supplied when running `update` on that installation. Pre-existing settings files remain protected by the conflict policy.

## Conflicts and backups

Default behavior is transactional and conservative: if an expected destination exists and is not owned by the ForgeOS manifest, the command aborts before writing.

```shell
python3 scripts/forgeos.py install --tool codex --scope local --target ./app
```

To explicitly replace collisions after backing them up:

```shell
python3 scripts/forgeos.py install --tool codex --scope local --target ./app --conflict backup
```

Backups are stored under `.forgeos/backups/`. On uninstall, ForgeOS restores the prior file whenever no later edits make restoration ambiguous. Updates also create recovery snapshots before replacing or removing managed files.

Do not treat `backup` as a substitute for project or user-profile backups.

## Status and drift

```shell
python3 scripts/forgeos.py status --tool all --scope global
```

`status` compares owned files against their hashes in the manifest. Any missing or modified file is reported as drift. This command is read-only.

For a local installation:

```shell
python3 scripts/forgeos.py status --tool all --scope local --target ./app
```

## Updating

```shell
python3 scripts/forgeos.py update --tool all --scope global
```

`update` uses the ForgeOS checkout from which the command runs. By default it refuses to overwrite a managed file that has been modified locally. `--conflict backup` explicitly authorizes backing it up and replacing it.

Inspect the updated checkout and run its tests before performing a global update.

## Uninstalling

```shell
python3 scripts/forgeos.py uninstall --tool all --scope global
```

Uninstallation:

- acts only on paths recorded in the manifest;
- never deletes application or sentinel files outside the manifest;
- preserves modified ForgeOS files instead of destroying them;
- restores a pre-existing backup when safe to do so;
- keeps the manifest if modified files prevent complete uninstallation.

Snapshots created during an update may contain user edits. They are therefore retained under `.forgeos/backups/` and their count is printed at the end of uninstall. Removal after inspection or archival remains a manual decision.

After reviewing a preserved file, restore its expected ForgeOS content or move it manually, then re-run `uninstall`.

## Isolated tests

Automated tests use `tempfile.TemporaryDirectory` and an injected `--home` root. They must never target the real user profile.

```shell
python3 -m unittest tests.test_installer -v
```

Isolated manual check example:

### Windows PowerShell

```powershell
$sandbox = Join-Path $env:TEMP 'forgeos-install-check'
New-Item -ItemType Directory -Force -Path $sandbox | Out-Null
python .\scripts\forgeos.py install --tool all --scope global --home $sandbox
python .\scripts\forgeos.py status --tool all --scope global --home $sandbox
python .\scripts\forgeos.py uninstall --tool all --scope global --home $sandbox
```

### macOS and Linux

```shell
sandbox="$(mktemp -d)"
python3 ./scripts/forgeos.py install --tool all --scope global --home "$sandbox"
python3 ./scripts/forgeos.py status --tool all --scope global --home "$sandbox"
python3 ./scripts/forgeos.py uninstall --tool all --scope global --home "$sandbox"
```

Afterwards, remove only the temporary directory you explicitly created.

## Validating the ForgeOS repository

From the root of the source checkout:

```shell
python3 scripts/claude_adapter.py --check
python3 scripts/gemini_adapter.py --check
python3 scripts/bootstrap.py
python3 tests/bootstrap.py
python3 -m unittest tests.test_installer -v
```

Structural checks do not prove authentication, network access, or remote permissions for Codex, Claude Code, Antigravity, or Gemini CLI.

## Safe troubleshooting

- `ForgeOS is not installed`: verify scope, target path, and effective home directory.
- `existing files would be replaced`: inspect the listed files; choose `backup` only after confirming the collision.
- `drift or conflicts`: diff the modified file against the ForgeOS source before backing up or updating.
- Invalid manifest: do not reconstruct it by hand; restore it from a trusted backup or inspect owned files before manual intervention.
