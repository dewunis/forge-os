---
name: release-management
description: Prepare and assess scoped software releases using verified evidence, explicit gates, approvals, artifacts, compatibility, and recovery plans. Use for release readiness or dry-run coordination; do not use to publish, tag, deploy, or mutate production without exact authorization.
---

# Release management procedure

## Establish the release contract

Confirm the release scope, source revision or candidate, target products and environments, owners, versioning policy, required evidence, approval gates, schedule constraints, compatibility expectations, and recovery strategy. Inspect the actual repository, manifests, lockfiles, version sources, changelog conventions, release automation, CI configuration, prior releases, migrations, documentation, and available results before assessing readiness.

Separate preparation, validation, approval, publication, deployment, and post-release verification. Authorization for one stage does not authorize another. Treat tags, hosted releases, registries, package indexes, EAS, app stores, remote environments, signing material, and production as external mutation boundaries.

## Build the evidence matrix

Map each required gate to an owner and observed evidence: implementation review, automated tests, builds, security, performance where applicable, data and migration compatibility, documentation, artifact identity or provenance, operational readiness, observability, support communication, and rollback or forward recovery. Record exact commands or external run identifiers only when actually observed.

Classify every gate as `passed`, `failed`, `blocked`, or `not-verified`. A draft, simulation, historical result, or absent check is not `passed`. Unresolved critical regressions, critical or high security findings, unsafe migrations, missing recovery, or unapproved breaking changes block readiness.

## Prepare bounded deliverables

When versioning is in scope, read and apply `../semantic-versioning/SKILL.md`. When changelog or release notes are in scope, read and apply `../changelog-generation/SKILL.md`. Keep those decisions traceable to the same evidence matrix without copying their procedures here.

Prepare only authorized release metadata and checklists. Preserve established formats and automation. Do not modify application code, tests, migrations, infrastructure, permissions, or security controls to satisfy a gate; return gaps to the owning specialist.

## Simulate and decide readiness

Use installed project commands and non-destructive dry-run modes only. Validate syntax, metadata consistency, version references, changelog links, build or packaging configuration, and documented release steps as the environment permits. Do not install missing tools.

Compare observed evidence with the release contract and report `ready-for-approval`, `changes-required`, or `blocked`. This is a recommendation, not approval or publication. Stop before merge, tag creation, release publication, package or artifact upload, EAS or store action, environment promotion, deployment, infrastructure change, or production mutation unless the current task explicitly authorizes that exact action and target.

## Hand off centrally

Return the candidate, proposed version, deliverables, evidence matrix, dry-run commands and results, blockers, known issues, compatibility and recovery assumptions, approvals pending, and residual risks to the Tech Lead and CTO. Distinguish executed checks from proposals and estimates.

Do not create a per-mission Markdown report or write ForgeOS centralized state. Critical release decisions require independent review; the Release Manager never self-approves them.
