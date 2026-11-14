---
name: ci-cd
description: Design, implement, and validate scoped container, automation, and CI/CD changes with reproducible builds, least privilege, protected secrets, verifiable evidence, and explicit deployment and recovery gates. Use for Docker, Docker Compose, GitHub Actions, reverse proxies, environment automation, artifacts, or authorized Infrastructure as Code; do not use for unapproved production or remote mutations.
---

# CI/CD

## Establish the delivery contract

Confirm scope, owners, target environments, application build and test commands, pinned runtimes and package managers, existing workflows, required checks, security gates, artifact destination, deployment authority, and recovery expectations. Inspect manifests, lockfiles, Docker and proxy configuration, scripts, workflows, environment templates, and Infrastructure as Code before changing them.

Treat secret values, production access, remote infrastructure, registries, EAS publication, public releases, branch protections, and deployment identities as approval-gated. Stop before mutation unless the current task explicitly authorizes the exact target and action.

## Design the smallest pipeline

Define triggers, concurrency, permissions, inputs, jobs, dependencies, caches, artifacts, retention, environments, approvals, failure behavior, and evidence. Reuse project commands and existing patterns. Keep builds deterministic and artifacts promotable where practical.

Place build, lint, type checks, tests, security analysis, packaging, deployment, post-deployment verification, and recovery gates according to actual risk and release policy. Do not add a stage merely to imitate another project.

## Protect boundaries

Use least-privilege workflow and deployment identities. Reference secrets only through approved stores and prevent them from entering source, build layers, logs, caches, artifacts, plans, state, or outputs. Pin or otherwise control third-party actions, base images, providers, and downloaded tooling according to project policy.

Keep environment-specific configuration explicit. Do not weaken required checks, review rules, branch protections, TLS, scans, isolation, or approvals to obtain a green run.

## Implement and validate

Change only delegated Dockerfiles, Compose files, proxy configuration, automation scripts, workflows, environment templates, or Infrastructure as Code. Preserve framework-native commands and coordinate shared manifests, migrations, schemas, or release artifacts with their owners.

Run the narrowest available non-destructive checks first: syntax and static validation, workflow or shell linting, Docker or Compose configuration, local builds and tests, proxy config tests, security scans, Terraform fmt or validate, and a read-only plan only when authorized. Do not install missing tools without approval.

An unexecuted workflow is not successful. Record each command or external run, target, exit status, result, limitations, and artifact evidence. Distinguish validation, dry run, staging execution, and production execution.

## Plan deployment and recovery

Before any authorized deployment, identify the exact target, immutable artifact, configuration, schema and data compatibility, approvals, health signals, stop conditions, rollback trigger, and operator. Verify that rollback is technically safe; otherwise define forward recovery or restore prerequisites and block unsafe promotion.

Production deployment, Terraform apply, registry push, public release, EAS publication, store submission, and remote infrastructure mutation require explicit current-task authorization.

## Hand off centrally

Return scope, changed paths, pipeline contract, security controls, commands and run evidence, artifacts, deployment status, recovery plan, residual risks, and unavailable checks to the Tech Lead and CTO. Coordinate security evidence with the Security Engineer and executable test stages with QA.

Do not create a per-mission Markdown report or write ForgeOS centralized state. Never claim an external run or deployment that was not verifiably executed.
