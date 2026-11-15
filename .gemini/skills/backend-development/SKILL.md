---
name: backend-development
description: Implement and validate scoped backend services and REST APIs using the project's installed framework, data model, security controls, and contracts. Use for Laravel or PHP, NestJS or TypeScript, and FastAPI or Python work; do not use for uncoordinated schema, frontend, mobile, infrastructure, or production changes.
---

# Backend development procedure

## Establish the implementation basis

1. Confirm the requested behavior, acceptance criteria, API consumers, data and side effects, failure behavior, security requirements, and delegated file ownership.
2. Inspect manifests and lockfiles, runtime and framework configuration, source and service boundaries, API specifications and clients, authentication and authorization, models and migrations, queues, cache, integrations, error handling, observability, tests, and configured validation commands.
3. Record the actual stack and versions. Use installed framework capabilities, libraries, persistence, queues, cache, and test tools; do not infer them from ForgeOS profiles or introduce replacements without approval.
4. Identify existing controllers, requests or DTOs, policies or guards, services, models or repositories, resources or serializers, errors, and tests before adding another abstraction.

## Map the request through the backend

Trace each requirement through request validation, authentication, authorization, application or domain behavior, transaction and persistence boundaries, side effects, response serialization, errors, logging, and tests. Preserve existing routes, payloads, status codes, error shapes, pagination, events, and integration contracts unless a coordinated change is approved.

For Laravel, prefer Form Requests, Policies or Gates, middleware, API Resources, Eloquent conventions, transactions, queues, jobs, events, notifications, cache and framework exception handling where they match existing project practice. Use Sanctum only when installed and appropriate.

For NestJS or FastAPI, follow the installed module, dependency-injection, validation, authorization, serialization, persistence, async, and exception-handling conventions. Do not recreate Laravel layers mechanically.

Stop and coordinate before changing a schema or migration, API contract, authentication model, dependency set, service boundary, infrastructure, production configuration, frontend, or mobile application. Coordinate data work with the installed Database Engineer, Tech Lead, and Software Architect, with serialized ownership for shared migration and model files. Never run a destructive migration without explicit authorization and rollback planning.

## Implement safely and proportionately

- Validate untrusted input at the framework boundary and enforce authorization server-side for every protected resource and action.
- Keep controllers and route handlers focused on transport concerns; place reusable business behavior in the project's established service or domain boundary without manufacturing layers for simple behavior.
- Use transactions for atomic invariants, keep them short, and account for concurrency, retries, idempotency, and post-commit side effects.
- Eager-load or shape queries deliberately, bound collections, and inspect likely N+1 paths. Move slow or retryable work to existing queues when correctness and user experience require it.
- Use existing Redis and cache abstractions with explicit ownership, invalidation, TTL, and safe serialization. Do not cache privileged data across users or tenants.
- Give external calls timeouts, safe authentication handling, validated responses, bounded retries, idempotency where applicable, and redacted diagnostics.
- Map failures consistently without exposing secrets, sensitive data, stack traces, SQL, tokens, or internal topology.
- Never disable security controls or weaken validation to satisfy a test. Never add or upgrade a dependency without authorization.

## Test and validate

Add or update the smallest relevant tests using installed tools: unit tests for deterministic behavior, feature or integration tests for validation and authorization, contract tests for stable API behavior, and failure-path tests for transactions, queues, cache, and external integrations.

Run the narrowest relevant tests first, then configured lint, type checks, static analysis, dependency audit, or broader suites according to risk. Use safe local or test environments, do not retrieve secrets, and do not trigger unauthorized external side effects. Record exact commands, exit codes, results, skipped checks, and environment limitations.

## Hand off evidence

Return concise evidence to the Tech Lead and CTO:

```text
Scope: behavior and delegated paths
Stack evidence: runtime, framework, versions, services, persistence, and test tools
Changes: validation, authorization, business logic, data access, responses, side effects, and tests
Contracts and data: compatibility, migration implications, transactions, and consumers
Validation: command -> result
Security and reliability: controls, N+1/blocking checks, retries, idempotency, and failure behavior
Residual risks: unavailable checks, schema ownership, external systems, or untested paths
Outcome: blocked | changes-required | ready-for-review
```

Do not create a per-mission Markdown report or write ForgeOS centralized state. Critical, data-sensitive, authentication, authorization, schema, or contract changes require independent review; implementation completion is not self-approval.
