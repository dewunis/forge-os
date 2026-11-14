# ForgeOS — Claude Code adapter

@../AGENTS.md

## Adapter contract

- `AGENTS.md` is the canonical ForgeOS governance file for Codex and Claude Code.
- `.codex/agents/*.toml` is the canonical source for the 17 specialist role definitions. `.claude/agents/*.md` is generated from it.
- `.agents/skills/*/SKILL.md` is the canonical source for reusable procedures. `.claude/skills/` is a generated Claude Code mirror.
- Do not edit generated agent or Skill files directly. Update the canonical source, run `python scripts/claude_adapter.py`, then run `python scripts/claude_adapter.py --check`.
- Technology profiles under `profiles/` remain catalogs only. Inspect target-project manifests and lockfiles before asserting a stack or version.
- Claude-specific settings are in `.claude/settings.json`. They do not grant production, release, secret, remote-infrastructure, or irreversible authority.
- Use only the minimum installed specialists needed for the active request. Critical changes still require independent review and human authorization where `AGENTS.md` requires it.
