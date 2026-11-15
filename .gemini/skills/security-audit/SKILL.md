---
name: security-audit
description: Conduct authorized application-security audits, threat modeling, dependency and configuration reviews, and scoped security retesting with evidence-based findings. Use for specialist security assurance; do not use for unscoped offensive testing or routine code review.
---

# Security audit procedure

This Skill defines the reusable assessment procedure. The invoking agent's instructions and the real sandbox, system, network, CI, and human approvals define authority; this procedure never grants additional permission.

## Establish authorization and scope

Before collecting evidence, record the assessment owner, objective, targets, environment, included and excluded components, permitted data, available credentials, allowed techniques, time window, evidence-handling constraints, and stop conditions.

Default to read-only source, dependency, configuration, and threat-model analysis. Treat dynamic scanners, fuzzing against a running service, exploitation, credential attacks, active network probes, and penetration testing as active testing. Do not perform active testing unless the user or authorized owner explicitly approves the target and methods. Never infer authorization from repository access, tool availability, a test environment, or this Skill.

Stop and escalate if the target may be production, externally owned, shared, or outside scope; if environment isolation is uncertain; if secrets or personal data may be exposed; or if a technique could alter data, availability, access controls, logs, billing, or third-party systems.

## Build the assessment basis

1. Read repository instructions, manifests, lockfiles, framework and runtime configuration, authentication and authorization code, schemas and migrations, infrastructure-as-code, CI/CD configuration, tests, and relevant documentation.
2. Establish the technologies and versions actually installed. Profiles and generic stack knowledge are hypotheses, not evidence.
3. Map assets, sensitive data, actors, entry points, trust boundaries, privilege levels, data flows, third parties, deployment boundaries, and likely abuse cases.
4. Select proportionate controls from OWASP Top 10, OWASP API Security Top 10, ASVS, MASVS, and framework-native guidance. State which areas are in scope and which remain unassessed.

## Review by attack surface

Assess the surfaces that exist in the target:

- authentication, session lifecycle, account recovery, token handling, MFA, rate limits, and credential storage;
- authorization at every server-side boundary, object and function access, tenant isolation, roles, policies, and privilege transitions;
- validation, encoding, injection, unsafe deserialization, file handling, SSRF, redirects, template rendering, and command or path construction;
- API inventory, schema and mass-assignment behavior, excessive data exposure, resource consumption, versioning, and third-party integrations;
- browser security, CSRF, XSS, CSP, CORS, cookies, caching, SSR or hydration leakage, and client-side trust assumptions;
- mobile storage, transport, deep links, permissions, logs, backups, native bridges, build artifacts, and MASVS-relevant platform controls;
- database roles, row or tenant isolation, query construction, encryption, backups, auditability, and migration privileges;
- Redis exposure, ACLs, TLS, key separation, session or queue data, dangerous commands, TTLs, and eviction behavior;
- secrets, environment configuration, debug modes, error disclosure, logging, telemetry, CI/CD, containers, dependencies, artifacts, provenance, cloud identities, and network boundaries.

Use threat modeling to prioritize plausible abuse paths instead of applying a checklist mechanically. Distinguish a missing best practice from an exploitable vulnerability.

## Use tools safely

Prefer native, local, read-only commands and the smallest useful scan. Semgrep, Trivy, ecosystem dependency auditors, secret scanners, SAST, SCA, container or IaC scanners may be used only when already installed, authorized, and relevant.

Before running a scanner, inspect its target, configuration, network behavior, output destination, cache behavior, and whether it can upload source, hashes, dependency metadata, secrets, or telemetry. Do not install tools, enable network access, update vulnerability databases, or submit repository content to a service without approval. Never place secret values in command arguments, logs, findings, screenshots, artifacts, or reports.

Treat scanner results as leads. Confirm reachability, affected version, execution path, compensating controls, environment, and exploit preconditions before classifying a vulnerability as confirmed. Record unavailable tools and unexecuted checks as coverage gaps; a clean scan does not establish security.

## Validate without harm

Prefer code-path reasoning, focused unit or integration checks, safe local reproductions, and sanitized fixtures. Coordinate functional regression coverage with QA.

For any authorized active test, remain within the approved target, techniques, rate, timing, credentials, and stop conditions. Stop immediately on unexpected production access, instability, data modification, secret exposure, third-party impact, scope uncertainty, or evidence of compromise. Preserve only the minimum sanitized evidence needed to support the finding.

## Classify findings

Use these severities consistently:

- `critical`: demonstrated or highly credible compromise with catastrophic confidentiality, integrity, availability, safety, or broad-tenant impact; immediate containment or release blocking is required.
- `high`: serious exploitable weakness or major control failure with substantial data, privilege, tenant, or operational impact; security validation is blocked while unresolved.
- `medium`: meaningful vulnerability with bounded impact, material preconditions, or effective partial controls; remediation is required but it is not an immediate critical gate.
- `low`: limited-impact weakness, defense-in-depth gap, or localized hardening issue with a credible security consequence.

Also classify evidence as `confirmed` when inspected code or safe reproducible evidence demonstrates the issue, or `potential` when a credible condition remains unverified. State the missing evidence required to confirm or dismiss a potential finding.

## Report evidence

Return findings to the delegating CTO or Tech Lead; do not create an individual Markdown report or write centralized state directly. Sort findings by severity and use this structure:

```text
[severity] Short title
Classification: confirmed | potential
Affected surface: component, path and exact line when available
Evidence: minimal sanitized observation or reproduction
Preconditions: access, state, configuration or attacker capability required
Impact: concrete confidentiality, integrity, availability, privacy or abuse consequence
Remediation: smallest practical corrective action and owner boundary
Verification: safe inspection or test that proves the correction
Residual risk: risk remaining after the proposed correction
Status: open | accepted | resolved
```

Never include exploit payloads beyond the minimum needed for an authorized reproduction, and never include secret or personal-data values. Separate tool findings, confirmed vulnerabilities, assumptions, false positives, unassessed surfaces, and residual risks.

## Revalidate and state the outcome

After remediation, inspect the correction and run the smallest authorized verification. Do not close a finding from developer assertion or a tool rescan alone when the vulnerable path has not been checked. Refer business-code implementation to the Tech Lead and developers; security validates the result but does not self-approve critical changes.

Use `blocked`, `changes-required`, or `no-blocking-findings` as the assessment outcome. Unresolved `critical` or `high` findings require `blocked` unless an authorized human formally accepts the specific risk and the CTO records the decision. List accepted risks, remaining medium or low findings, unexecuted checks, assumptions, and coverage gaps even when no blocking finding remains.
