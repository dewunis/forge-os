# ForgeOS

**English** | [Français](README.fr.md)

ForgeOS is a multi-agent software engineering organization usable with OpenAI Codex, Claude Code, Google Antigravity (`agy` CLI & Antigravity IDE), and Gemini CLI. It provides shared CTO governance, 17 specialists, 16 reusable procedures, technology profiles, and a safe Python installer for Windows, macOS, and Linux.

ForgeOS is neither an operating system nor an application framework. It structures agent work around the code and conventions already present in a project.

## Principles

- Existing code, tests, manifests, and configurations take precedence over ForgeOS profiles.
- The CTO invokes only the specialists needed for the active request and retains technical arbitration.
- Sensitive, production, and release operations remain gated on human authorization.
- Significant changes require independent review.
- Technologies, dependencies, and models are never installed or replaced implicitly.

## Architecture

`AGENTS.md` defines the shared governance. Canonical roles live under `.codex/agents/` and canonical Skills live under `.agents/skills/`. The Claude Code, Antigravity, and Gemini CLI adapters generate their native agents and Skill mirrors under `.claude/` and `.gemini/` (`.gemini/agents/` for Gemini CLI, `.gemini/antigravity-agents/` discovered via `.agents/agents.json` locally and `~/.gemini/config/` globally for Antigravity).

```text
User
  └─ ForgeOS CTO
      ├─ scoping: Product Manager, Software Architect, UI/UX Designer
      ├─ delivery: Tech Lead and specialized engineers
      ├─ assurance: QA, Security, Performance, Code Reviewer
      └─ documentation and release: Technical Writer, Release Manager

ForgeOS sources
  ├─ AGENTS.md
  ├─ .codex/agents/*.toml
  └─ .agents/skills/*/SKILL.md
        ├─ generated adapter: .claude/agents + .claude/skills
        └─ generated adapter: .gemini/agents + .gemini/antigravity-agents + .gemini/skills (+ .agents/agents.json)
```

Profiles in `profiles/` are a technology catalog only, never evidence of versions installed in a target project.

## Agents

ForgeOS includes 17 subagents:

| Domain | Agents |
| --- | --- |
| Product & architecture | Product Manager + Business Analyst, Software Architect, Tech Lead |
| Engineering | Frontend Engineer, Backend Engineer, Mobile Engineer, Database Engineer, AI/LLM Engineer |
| Experience | UI/UX Designer |
| Platform & operations | Platform / DevOps Engineer, Reliability Engineer |
| Quality & security | QA Engineer, Security Engineer, Performance Engineer, Code Reviewer |
| Documentation & delivery | Technical Writer & API Documentation Engineer, Release Manager |

The CTO is the root orchestrator and is not counted among these 17 subagents.

## Skills

The 16 Skills cover: frontend, backend, mobile, and AI development; database migrations; UI/UX; CI/CD; incident response; performance and security audits; API documentation; software testing; code review; release management; semantic versioning; changelog generation.

Each Skill uses a mandatory `SKILL.md` manifest. Copies under `.claude/skills/` and `.gemini/skills/` are generated mirrors for Claude Code, Antigravity, and Gemini CLI discovery and must not be edited directly.

## Covered technologies

- Backend: Laravel/PHP, NestJS/TypeScript, FastAPI/Python.
- Web: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Nuxt, and Vue.
- Mobile: Expo, React Native, Expo Router, React Native Reusables, NativeWind, and Uniwind.
- Data: PostgreSQL, MySQL/MariaDB, Redis, and mobile SQLite where justified.
- Platform: Docker, GitHub Actions, Linux, Nginx, Caddy, and scoped Terraform.
- Quality: Pest/PHPUnit, Vitest, Jest, Playwright, Maestro, Lighthouse, k6, and native project tooling.

ForgeOS installs none of these technologies. It detects and respects the versions actually present.

## Prerequisites

- Python 3.9 or later for the installer, with zero external dependencies.
- Codex, Claude Code, Google Antigravity (`agy` CLI / Antigravity IDE), and/or Gemini CLI installed and authenticated separately.
- Python 3.11 or later for the source validator `scripts/bootstrap.py`, which uses `tomllib`.

## Installation

Local installation into a project:

```shell
python scripts/forgeos.py install --tool all --scope local --target /path/to/project
```

Global installation for the current user:

```shell
python scripts/forgeos.py install --tool all --scope global
```

Available `--tool` values: `codex`, `claude`, `gemini` (targets Antigravity `agy` CLI / Antigravity IDE and Gemini CLI), or `all`. The `local` scope writes to the target project (including `.agents/agents.json` and, when `gemini` is installed standalone, `.agents/skills.json`); the `global` scope uses the home directory resolved by Python and native folders `.codex`, `.agents/skills`, `.claude`, `.gemini`, and `.gemini/config`.

Settings files that affect sandboxing, approvals, or permissions are not installed by default. Installing them requires explicit consent:

```shell
python scripts/forgeos.py install --tool all --scope local --target /path/to/project --include-settings
```

If a target file already exists, installation stops without mutating anything. To explicitly request backups before replacement:

```shell
python scripts/forgeos.py install --tool all --scope local --target /path/to/project --conflict backup
```

See [docs/installation.md](docs/installation.md) for destination paths, backups, exit codes, and Windows, macOS, and Linux examples.

The Git workflow, validation gates, and release procedure are described in
[docs/release-process.md](docs/release-process.md). Deliverable changes are
summarized in [CHANGELOG.md](CHANGELOG.md).

## Usage and maintenance

```shell
python scripts/forgeos.py status --tool all --scope global
python scripts/forgeos.py update --tool all --scope global
python scripts/forgeos.py uninstall --tool all --scope global
```

For a local installation, add `--target /path/to/project`. Tool selection and scope must match the manifest created at install time.

The installer maintains `.forgeos/install-manifest.json` with hashes of owned files. Any user modification is flagged as drift and is neither overwritten nor deleted without explicit choice. Uninstallation leaves files outside the manifest untouched and restores pre-existing backups when it can do so without data loss.

## Repository validation

```shell
python scripts/claude_adapter.py --check
python scripts/gemini_adapter.py --check
python scripts/bootstrap.py
python tests/bootstrap.py
python -m unittest tests.test_installer -v
```

Installer tests run strictly in temporary directories. They never modify real global configuration.

## Security

- Never copy secrets, tokens, or real `.env` files into ForgeOS.
- Agent instructions are governance, not a security boundary.
- Effective permissions depend on host sandboxing, identities, Git rules, CI, and protected environments.
- No push, merge, tag, deployment, or production mutation is implicitly authorized.
- `--include-settings` and `--conflict backup` are explicit consents to additional mutations; always inspect scope before running them.

## Limitations

- The installer does not configure Codex/Claude/Gemini authentication or remote permissions.
- Technology profiles are guidance catalogs only and install no dependencies.
- Existing user governance can conflict with ForgeOS; the default behavior is to abort without writing.
- Recovery snapshots created during an update are retained after uninstall when they may hold user edits; the CLI prints their location for manual cleanup.
- Cross-platform behavior relies on the Python standard library and should also be verified in each target OS's native CI before public release.
- Native settings and formats for Codex, Claude Code, Antigravity, and Gemini CLI can evolve; validate CLI upgrades before rolling them out broadly.

## License

ForgeOS is distributed under the MIT License. See [LICENSE](LICENSE).

## Contributing

1. Preserve `AGENTS.md`, `.codex/agents/`, and `.agents/skills/` as sources of truth.
2. Regenerate the Claude and Gemini/Antigravity adapters with `python scripts/claude_adapter.py` and `python scripts/gemini_adapter.py`.
3. Do not manually edit generated files under `.claude/agents/`, `.claude/skills/`, `.gemini/agents/`, `.gemini/antigravity-agents/`, or `.gemini/skills/`.
4. Add or update isolated tests for any installer or adapter change.
5. Run all validation commands above and report only directly observed results.
6. Never override application source-code conventions in the name of ForgeOS internal naming rules.

New commits follow Conventional Commits and land on `dev`. Promotion to `main`,
tagging, and publishing releases remain gated by the reviews and approvals
described in the release process.
