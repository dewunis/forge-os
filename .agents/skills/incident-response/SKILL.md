---
name: incident-response
description: Diagnose and coordinate scoped service incidents with preserved evidence, explicit authorization gates, hypothesis-driven analysis, safe remediation, and verified recovery. Use for operational triage, metrics/log/trace analysis, incident escalation, rollback or restoration planning, post-deployment failures, runbook improvement, and blameless postmortem inputs; do not use for unapproved production actions.
---

# Incident Response

## Establish command and authorization

Confirm the incident owner, affected services and environments, user and business impact, current status, communication channel, available responders, production-access boundary, and next checkpoint. Record timestamps with timezone and distinguish reported symptoms from observed facts.

Production commands, restarts, reloads, scaling, traffic changes, rollback, failover, restore, remote mutation, privileged access, and cloud spending require explicit authorization for the exact target and action. Analysis permission alone does not authorize remediation.

## Preserve and bound

Protect logs, traces, metrics, alerts, audit events, deployment identifiers, configuration versions, and relevant artifacts. Never delete or alter investigation evidence. Use only authorized data and redact secrets, credentials, personal data, and unnecessary payloads.

Bound the time range, blast radius, affected user journeys, dependencies, recent changes, data-integrity risk, and whether impact is ongoing. Escalate security indicators to the Security Engineer and database integrity or recovery concerns to the Database Engineer.

## Diagnose with hypotheses

Build a timeline from correlated, time-qualified evidence. List hypotheses with supporting and contradicting evidence, confidence, and the next safe discriminating check. Inspect metrics, logs, traces, health checks, capacity, dependencies, deployments, configuration, queues, databases, caches, and external services according to symptoms.

Do not promote correlation or a plausible narrative to confirmed root cause. When telemetry is stale, sampled, incomplete, inconsistent, or unavailable, state the limitation and choose the safest next observation.

## Coordinate remediation

Prefer the smallest reversible mitigation that reduces impact without destroying evidence. For each proposed action, state owner, target, expected effect, risk, prerequisites, authorization, stop condition, rollback or forward-recovery path, and verification signal.

Coordinate pipeline or deployment mechanisms with the Platform / DevOps Engineer, database operations with the Database Engineer, architectural changes with the Software Architect, and production authority with the CTO. Never execute a restart, rollback, restore, failover, or production change without explicit approval.

## Verify recovery

After an authorized action, verify service-level and user-impact indicators, health and readiness, dependency health, error rates, latency, saturation, queue behavior, data integrity where relevant, and alert state over an agreed observation window. Compare against baseline or SLO expectations when available.

Distinguish mitigation, service recovery, incident resolution, and root-cause confirmation. Do not declare resolution from a command exit code, a single healthy check, or disappearing alerts alone.

## Learn and hand off centrally

Return a sanitized timeline, impact, evidence, hypotheses, confirmed findings, actions and authorizations, verification results, residual risk, owners, and next checkpoints to the Tech Lead and CTO. Propose runbook improvements and blameless postmortem inputs focused on contributing system conditions, detection, response, recovery, and verifiable corrective actions.

Do not create a per-mission Markdown report or write ForgeOS centralized state. Do not include secrets or sensitive raw evidence in the handoff.
