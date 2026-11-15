# ForgeOS — Antigravity & Gemini CLI adapter

@../AGENTS.md

## Adapter contract

- `AGENTS.md` is the canonical ForgeOS governance file for Codex, Claude Code, Google Antigravity (`agy` CLI & Antigravity IDE), and Gemini CLI.
- `.codex/agents/*.toml` is the canonical source for the 17 specialist role definitions. `.gemini/agents/*.md` is generated from it.
- `.agents/skills/*/SKILL.md` is the canonical source for reusable procedures. `.gemini/skills/` is a generated Gemini CLI mirror.
- Antigravity discovery uses `.agents/agents.json` (plus `.agents/skills.json` when installed standalone) in a workspace, or `~/.gemini/config/` (`GEMINI.md`, `agents.json`, `skills.json`) globally to point to `.gemini/antigravity-agents/*.md` (`subagent: true`, `mainAgent: false`, least-privilege `tools:`), while `.gemini/agents/*.md` uses Gemini CLI's standalone schema and tool names.
- Do not edit generated agent or Skill files directly. Update the canonical source, run `python scripts/gemini_adapter.py`, then run `python scripts/gemini_adapter.py --check`.
- Technology profiles under `profiles/` remain catalogs only. Inspect target-project manifests and lockfiles before asserting a stack or version.
- Gemini-specific settings are in `.gemini/settings.json`. They do not grant production, release, secret, remote-infrastructure, or irreversible authority.
- Use only the minimum installed specialists needed for the active request. Critical changes still require independent review and human authorization where `AGENTS.md` requires it.
