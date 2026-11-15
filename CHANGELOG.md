# Changelog

**English** | [Français](CHANGELOG.fr.md)

All notable changes to ForgeOS are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this project adheres to [Semantic Versioning](https://semver.org/).

## Unreleased

### Added

- Dual-target Google Antigravity (`agy` CLI & Antigravity IDE) and Gemini CLI adapter
  generating `.gemini/agents/*.md` (Gemini CLI schema and least-privilege native tools),
  `.gemini/antigravity-agents/*.md` (`subagent: true`, `mainAgent: false`, least-privilege
  `tools:`, and `skills: ../skills/<skill>` frontmatter), the `.gemini/skills/` mirror,
  `.agents/agents.json`, `.gemini/GEMINI.md`, `.gemini/settings.json`, and the hardened
  `scripts/gemini_adapter.py` sync script (atomic writes, exhaustive role classification,
  and broken-symlink detection and cleanup).
- Support for `--tool gemini` (and inclusion in `--tool all`) in the Python installer
  `scripts/forgeos.py` and isolated tests, including `.agents/agents.json` ->
  `.gemini/antigravity-agents` / `.agents/skills.json` for local installs and
  `~/.gemini/config/{GEMINI.md,agents.json,skills.json}` for global installs.
- Coverage of Google Gemini API, Interactions API, Gemini Live API, and Google GenAI SDK
  (`google-genai` / `@google/genai`) across `ai-llm-engineer`, `ai-development`,
  `AGENTS.md`, `profiles/python-ai.yaml`, and `docs/technology-catalog.md`.
- Bilingual English-by-default documentation with French companion files
  (`README.md` / `README.fr.md`, `docs/installation.md` / `docs/installation.fr.md`,
  `docs/release-process.md` / `docs/release-process.fr.md`, `CHANGELOG.md` / `CHANGELOG.fr.md`)
  and cross-link validation in `scripts/bootstrap.py`.
- Multi-OS GitHub Actions CI workflow (`.github/workflows/ci.yml`) running all ForgeOS
  checks on Linux, macOS, and Windows with least-privilege permissions (`contents: read`,
  `persist-credentials: false`), plus validation in `scripts/bootstrap.py`.
- Hardening of `scripts/claude_adapter.py` with atomic writes and broken-symlink
  detection and cleanup, covered alongside `scripts/gemini_adapter.py` in unit tests.

## 0.1.0 - 2026-11-14

### Added

- Shared CTO governance for Codex and Claude Code, with 17 specialized subagents
  and explicit responsibility boundaries.
- 16 reusable Skills covering development, quality, security, performance,
  documentation, and release preparation.
- Claude Code adapter generating native agents and the Skill discovery mirror
  from canonical ForgeOS sources.
- Advisory technology profiles for Laravel, Next.js, Nuxt, NestJS, Expo, and
  multi-stack products, without implicit installation or upgrades.
- Dependency-free Python 3 installer with `install`, `update`, `status`, and
  `uninstall` commands for Codex, Claude Code, or both, in local or global scope.
- Conflict handling, explicit backups, ownership manifest, drift detection, and
  uninstallation scoped strictly to ForgeOS-owned files.
- Structural validators, Claude Code synchronization checks, and isolated
  installer lifecycle tests.
- Project distribution under the MIT License.

### Known limitations

- Installer compatibility was executed natively on Windows only; macOS and
  Linux remain to be verified in their environments.
- Structural checks do not prove all runtime behavior: Claude Code discovered
  all 17 agents, while dynamic Skill execution and model behavior remained
  unverified due to expired authentication.
- ForgeOS does not configure authentication, GitHub protections, remote
  permissions, or production environments.
- Technology profiles are guidance only and never prove a target project's
  installed stack or versions.
- Codex and Claude Code settings capable of changing permissions remain opt-in
  and require explicit consent.
