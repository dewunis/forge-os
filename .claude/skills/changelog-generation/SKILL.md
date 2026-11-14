---
name: changelog-generation
description: Create or update changelogs and release notes from verified repository and release evidence while preserving project conventions. Use for user-facing change histories; do not fabricate entries, duplicate canonical docs, publish releases, or expose sensitive data.
---

# Changelog generation procedure

## Establish the evidence and format

Inspect the existing changelog or release-note convention, audience, current and target versions, comparison range, repository history or diff, merged changes, issue or pull-request links when locally or explicitly available, tests, migrations, deprecations, known issues, security disclosure policy, and documentation. Prefer the canonical existing changelog over a new parallel file.

## Draft traceable entries

Include only verified changes in categories supported by the project, such as Added, Changed, Deprecated, Removed, Fixed, and Security. Describe user, developer, operator, compatibility, migration, or recovery impact at the appropriate level. Deduplicate equivalent changes and preserve identifiers or contributor attribution only when evidenced.

Separate implemented changes from planned, experimental, reverted, or unverified work. Do not infer release dates, versions, fixes, features, links, contributors, test results, deployment status, or security details. Follow disclosure policy for vulnerabilities and never include secrets, tokens, personal data, private incident details, or exploit-enabling information.

## Validate and hand off

Check version headings, comparison links, anchors, references, ordering, duplicate entries, migration and deprecation notes, and consistency with the proposed version and verified change set. Use existing lint or link-check tooling when installed; record anything not checked.

Return changed canonical paths, evidence sources, entries added or omitted, validation results, unresolved classification questions, sensitive-data handling, and publication dependencies. A changelog draft is not a published release. Do not tag, publish, or deploy. Do not create a per-mission Markdown report or write ForgeOS centralized state.
