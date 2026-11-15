---
name: api-documentation
description: Create and maintain evidence-based technical and API documentation from verified code, tests, contracts, schemas, and configuration. Use for Markdown, OpenAPI, JSON Schema, API references, setup or developer guides, ADRs, and runbooks; do not use to invent behavior or change implementation.
---

# API documentation procedure

## Establish the documentation basis

1. Confirm the audience, task, document type, scope, supported versions or platforms, authorized files, acceptance criteria, and whether the output describes implemented, planned, experimental, deprecated, or removed behavior.
2. Inspect the existing documentation tree, navigation, terminology, style, generated-doc workflow, and canonical location. Update an existing authoritative document whenever it can absorb the change without confusion; create a new file only for a distinct durable audience need.
3. Build an evidence map from the relevant code paths, tests, routes, OpenAPI or JSON Schema contracts, models or DTOs, configuration, manifests, lockfiles, migrations, and approved architecture or operational records. Record conflicts and missing evidence instead of resolving them by assumption.
4. Treat verified implementation and approved contracts as the source of truth. A plan, issue, comment, profile, stale document, or generated example is not proof of current behavior by itself.

## Draft from evidence

Write only claims supported by the evidence map. Keep status and applicability explicit, including version, environment, feature flag, platform, authentication context, or deprecation state when relevant.

For an API surface, cover only the evidenced contract:

- purpose, method, path, authentication and authorization expectations;
- path, query, header, cookie, and body inputs with requiredness, types, formats, constraints, defaults, and nullability when verified;
- response status codes, content types, schemas, headers, pagination or rate-limit behavior, and error shapes when verified;
- side effects, idempotency, concurrency, consistency, or asynchronous behavior when they are part of the observed or approved contract;
- sanitized request and response examples that conform to the contract, clearly labeled as representative unless captured from an authorized verified test.

For other documentation, preserve the same evidence discipline:

- Installation and developer guides identify prerequisites, supported versions, configuration placeholders, exact working directory, commands, expected checkpoints, and safe troubleshooting boundaries.
- Architecture documentation describes approved components, boundaries, dependencies, data flows, and constraints without creating decisions through the document.
- ADRs record the decision owner, status, context, considered options, decision, consequences, and supersession relationship supplied by the approved architecture process.
- Runbooks define trigger, preconditions, authorization, safety checks, ordered actions, verification, stop conditions, rollback or recovery, escalation, and ownership from approved operational procedures.

Use the project's established format, filenames, terminology, link style, heading hierarchy, and code-fence conventions. Do not apply ForgeOS naming preferences to application code or tool-required files.

## Protect sensitive and uncertain information

Use placeholders for tokens, credentials, domains, account identifiers, personal data, connection strings, and environment-specific values. Never copy secrets or production records into documentation, examples, commands, fixtures, screenshots, or specifications.

Do not present a synthetic example, unexecuted command, proposed response, inferred default, or planned feature as observed reality. Label representative examples, estimates, planned work, deprecations, and unverified claims precisely. When evidence conflicts, document the confirmed portion and return the discrepancy to the owner.

## Validate the deliverable

Use only already-installed and project-configured tools. Validate proportionately:

- parse OpenAPI, JSON Schema, YAML, JSON, and other structured artifacts;
- run existing Markdown lint, documentation build, schema validation, or link-check commands;
- verify internal anchors, relative paths, navigation, and referenced files;
- execute safe setup or developer commands in an isolated environment when authorized and practical;
- compare endpoint, parameter, response, error, and authentication documentation against routes, DTOs or schemas, tests, and implementation;
- confirm examples are schema-compatible and sanitized.

Record each command, working directory, exit code, and result. If a command, example, link, or behavior is not checked, mark it `not-verified` with the reason. Do not invent passing results or install missing validators without approval.

## Hand off centralized evidence

Return a concise evidence block to the Tech Lead and CTO:

```text
Scope: audience, document type, versions/platforms, and delegated files
Sources: code, tests, contracts, schemas, configuration, and existing docs inspected
Status: implemented | planned | experimental | deprecated | removed | mixed
Changes: canonical documents or specifications created/updated and why
Validation: exact command/check -> result; links/examples checked
Discrepancies: documentation, contract, test, configuration, or implementation conflicts
Not verified: claim, command, link, or example and reason
Sensitive-data handling: placeholders and sanitization applied
Residual risks: stale sources, missing owner evidence, publication or release dependency
Outcome: blocked | changes-required | ready-for-review
```

Do not create a per-mission Markdown report or write ForgeOS centralized state. Critical API, architecture, security-sensitive, operational, deprecation, or release documentation requires independent review and the appropriate owner approval.
