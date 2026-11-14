# ForgeOS architecture

## Current phase: CTO + Product Manager/Business Analyst + Software Architect + Tech Lead + UI/UX Designer + Frontend Engineer + Backend Engineer + Mobile Engineer + Database Engineer + AI/LLM Engineer + Platform/DevOps Engineer + Reliability Engineer + Performance Engineer + Technical Writer/API Documentation Engineer + Release Manager + QA Engineer + Security Engineer + Code Reviewer

`User -> Codex or Claude Code root session (CTO) -> Product Manager/Business Analyst for product clarification -> Software Architect for design -> UI/UX Designer for experience and interface contracts when needed -> Tech Lead for delivery coordination -> Frontend, Backend, Mobile, Database, AI/LLM, Platform/DevOps, Reliability, or Performance Engineer for scoped implementation and analysis -> QA Engineer for test evidence -> Security Engineer for authorized security assurance -> Technical Writer/API Documentation Engineer for verified technical and API documentation when needed -> Code Reviewer for independent review -> Release Manager for gated release preparation`. The 17 project-scoped role definitions are canonical in `.codex/agents/*.toml`. `scripts/claude_adapter.py` generates the equivalent native Claude Code definitions in `.claude/agents/*.md`; generated files are never edited directly. Small, already-clear requests may skip unnecessary roles.

## Target organization (18 functions)

Direction: CTO (root), Software Architect, Tech Lead, Product Manager + Business Analyst.
Development: Frontend Engineer, Backend Engineer, Mobile Engineer, Database Engineer, AI/LLM Engineer, UI/UX Designer.
Operations: Platform + DevOps Engineer, Cloud + SRE + Production Support Engineer.
Quality: QA + QA Automation Engineer, Application Security + Pentest Engineer, independent Code Reviewer, Performance Engineer.
Documentation: Technical Writer + API Documentation Engineer.
Release: Release Manager.

Full-Stack is deliberately not a separate agent; Tech Lead coordinates Frontend + Backend.

## Responsibility chain

User request -> CTO triage -> Product Manager for product ambiguity -> Architect for structural design -> installed UI/UX Designer for user journeys and interface contracts when needed -> Tech Lead for engineering delivery -> installed Frontend Engineer for web scope, installed Backend Engineer for service scope, installed Mobile Engineer for Expo and React Native scope, installed Database Engineer for schema and data scope, installed AI/LLM Engineer for model and retrieval scope, installed Platform/DevOps Engineer for containers, environments, automation, and CI/CD scope, installed Reliability Engineer for observability, operational readiness, incidents, continuity, and recovery scope, installed Performance Engineer for profiling, benchmarks, bottleneck diagnosis, and measured optimization, or future specialists when installed -> QA and installed Security Engineer as risk demands -> installed Reliability Engineer for post-deployment health verification -> installed Performance Engineer for performance validation when required -> installed Technical Writer/API Documentation Engineer for verified documentation and specifications when required -> independent Code Reviewer -> authorized merge -> installed Release Manager for versioning, changelog, evidence gates, and dry-run preparation -> separately authorized publication or deployment -> SRE verification.

Small low-risk tasks skip unnecessary roles. Require independent review for critical work. External safeguards enforce Git permissions, production access, protected environments and human approvals. No AGENTS instructions alone can enforce these controls.

## Stack knowledge

`profiles/*.yaml` declares preferred *technology families*. It is a human- and agent-readable catalog, not a native Codex or Claude Code feature. Target project lockfiles/manifests win over preferred versions; do not auto-upgrade or install. Reusable Skills are canonical in `.agents/skills/` and mirrored into `.claude/skills/` for Claude Code discovery.

## Concurrency

Default max open subagent threads = 3 when installed. Never delegate simultaneous writes to overlapping files, manifests, migrations, generated clients, or shared API contracts. Independent read-only investigation may run in parallel.

## Installation layer

`scripts/forgeos.py` renders the repository sources into native Codex and/or Claude Code locations. Local installations use the target project; global installations use the current user's home directory and store shared ForgeOS resources under `~/.forgeos/`.

The repository remains the source of truth. Installed files are tracked by `.forgeos/install-manifest.json` with content hashes and optional backup paths. An unmanaged collision or managed-file drift blocks mutation by default. Updates snapshot changed files before replacement, and uninstall removes only intact files recorded in the manifest. Tool settings that affect models, sandboxing, approvals, or permissions are opt-in through `--include-settings`.

## Operational state and activity

`.ai/state.json` is the canonical snapshot of current ForgeOS operational state. `.ai/activity.jsonl` is the append-only activity history, with one valid JSON object per line.

The CTO root is the sole writer to both files. Specialists return their status and evidence to the CTO; they never write these files directly. The CTO serializes state updates to avoid conflicting writes.

Do not generate a Markdown report automatically for each mission. The final user response carries the mission summary, while the state and activity files retain only concise operational metadata. Never store secrets in either file.
