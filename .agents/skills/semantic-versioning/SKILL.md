---
name: semantic-versioning
description: Propose and validate semantic versions from verified public changes and the project's actual version policy. Use for release bump classification, prereleases, or compatibility decisions; do not create tags, publish releases, or invent change impact.
---

# Semantic versioning procedure

## Determine the governing policy

Inspect the current authoritative version, version files, package metadata, tags when available, release policy, supported public API or behavior, and prior version conventions. Confirm whether the project follows SemVer, has a zero-major policy, uses synchronized package versions, prerelease identifiers, or another approved exception. Do not impose SemVer where the project explicitly uses a different scheme.

## Classify verified impact

Build a change set from verified diffs, contracts, migrations, tests, documentation, and accepted decisions. For SemVer projects, propose:

- `major` for incompatible public API or behavior changes;
- `minor` for backward-compatible public functionality;
- `patch` for backward-compatible fixes.

Treat internal refactors, dependency changes, performance work, security fixes, schema changes, and configuration changes according to their actual externally observable compatibility impact, not their labels. Flag ambiguous impact and pre-1.0 interpretation for owner decision. Include prerelease identifiers or build metadata only when they match established policy.

## Validate the proposal

Check that the proposed version is greater than the current version, syntactically valid for the governing policy, consistent across authoritative version locations, and compatible with release branches, package constraints, generated artifacts, documentation, and migration guidance. Do not edit unrelated version occurrences or lockfiles merely to force consistency.

Return the current version, proposed version, bump class, evidence per material change, policy assumptions, incompatible or ambiguous items, files that would require an authorized update, and confidence. Label it `proposed` until approved. Never create or move a tag, publish, deploy, or claim release approval.

Do not create a per-mission Markdown report or write ForgeOS centralized state.
