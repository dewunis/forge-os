# Permissions and safety boundaries

| Operation | CTO bootstrap | Future enforcing control |
| --- | --- | --- |
| Read source/config | Yes, within sandbox | filesystem permissions |
| Modify local files | Only requested scope | sandbox/worktree controls |
| Execute commands | Only within active Codex approval/sandbox policy | CLI sandbox |
| Install dependencies | Only when necessary and permitted | restricted network/sandbox |
| Access secrets | No by default | secret store and role-specific IAM |
| Change infrastructure config | Proposal first; no production changes | protected environments |
| Git push | Requires task authorization | GitHub token scopes |
| Merge PR | Not granted by this repo | branch protection/review rules |
| Annotated tag | Only with explicit release approval | protected tags/credentials |
| GitHub release | Only with explicit approval | workflow permissions |
| Production deploy | Forbidden without explicit approval | GitHub environment reviewers/IAM |

**Security reminder:** text instructions are not access controls. In future phases enforce actual restrictions in GitHub branch rules, CI workflow permissions, OS/containers, identity access and secret handling. Do not store tokens in this repository or in ForgeOS state or activity files.

Codex follows `.codex/config.toml` plus the active host sandbox and approval policy. Claude Code follows `.claude/settings.json`, Gemini CLI follows `.gemini/settings.json` and Policy Engine rules in `.gemini/policies/forgeos.toml` (plus least-privilege tool allowlists on `.gemini/agents/*.md`), and Google Antigravity (`agy` CLI & Antigravity IDE) follows `subagent`, `mainAgent`, and least-privilege `tools` frontmatter on `.gemini/antigravity-agents/*.md` discovered via `.agents/agents.json` or `~/.gemini/config/agents.json`; their project rules ask before common publication, release, deployment, and infrastructure-mutation commands and deny reads and writes of common `.env` secret paths. These settings are defense in depth, not a substitute for credential separation, branch protection, protected environments, or human approval.

An operation that needs approval is not automatically safe merely because the model asks permission. Review scope, environment, rollback plan and evidence.

The ForgeOS installer follows the same boundary. It does not install Codex, Claude, or Antigravity / Gemini settings by default, refuses unmanaged file collisions, and records only its own files in an ownership manifest. `--include-settings` and `--conflict backup` are explicit consent flags, not blanket authorization for production, credentials, remote systems, or unrelated files.
