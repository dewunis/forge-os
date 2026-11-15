---
name: database-migration
description: Plan, implement, and validate scoped relational database migrations with compatibility, integrity, performance, and recovery evidence. Use for PostgreSQL, MySQL or MariaDB, Laravel migrations, indexes, constraints, and data evolution; do not use for unauthorized destructive, restore, or production operations.
---

# Database migration procedure

## Establish the migration basis

1. Confirm the requested data outcome, affected applications and versions, authorized environment, data sensitivity, expected volume, availability constraints, ownership, and acceptance criteria.
2. Inspect the actual engine and version, schema, migration history, models and queries, constraints and indexes, transaction boundaries, deployment process, representative data characteristics, backup and restoration evidence, tests, and framework conventions.
3. Identify dependencies across application releases, jobs, events, reports, caches, replicas, and integrations. Coordinate shared contracts and migration files with the Tech Lead and Backend Engineer.
4. Stop if the target, environment, authorization, recovery owner, or compatibility requirements are ambiguous. Never retrieve or display connection strings, credentials, or production records.

## Design a progressive path

Prefer expand-and-contract for consequential changes:

1. **Expand:** add nullable or otherwise compatible structures, indexes, and constraints in a way old and new application versions can tolerate.
2. **Migrate:** backfill in bounded, observable, resumable, idempotent batches with explicit throttling, retry, lock, and failure behavior.
3. **Verify:** compare counts and invariants, validate constraints, inspect errors and plans, and confirm both application versions remain compatible.
4. **Switch:** move writes and reads through the coordinated application rollout, preserving a defined fallback window.
5. **Contract:** remove obsolete columns, indexes, code paths, or compatibility logic only as a separate explicitly authorized step after evidence and retention requirements are satisfied.

For every step, document preconditions, expected lock and runtime behavior, transaction scope, engine-version limitations, validation queries, stop conditions, monitoring owner, roll-forward, rollback feasibility, and whether any data or semantics would be lost. Never infer reversibility from a framework `down` method alone.

## Implement within ownership

- Follow the installed framework and engine conventions; keep migrations deterministic and avoid application-runtime assumptions that will not exist during deployment.
- Preserve primary, foreign-key, unique, check, not-null, and tenant-integrity invariants. Sequence constraint creation and validation to avoid unsafe gaps or excessive locks.
- Justify indexes from representative access patterns and execution plans. Account for selectivity, column order, write amplification, storage, maintenance, concurrent or online build support, and redundant indexes.
- Keep data changes bounded and restartable. Avoid loading full tables into application memory, long transactions, implicit commits, unstable ordering, and per-row application loops when safe set-based or batched work exists.
- Coordinate Eloquent and Query Builder changes, eager loading, transaction behavior, and N+1 prevention with the Backend Engineer. Do not modify backend business logic or APIs without delegation.
- Treat Redis changes separately from relational migrations: define key versioning, TTL, invalidation, compatibility, memory impact, and safe rollback; never use broad destructive Redis commands without explicit authorization.

## Validate safely

Run the migration first in an isolated representative environment using synthetic or approved sanitized data. Validate forward behavior, actual rollback or roll-forward feasibility, schema and data invariants, application compatibility, query plans, lock and transaction behavior, runtime and resource impact, failure recovery, and rerun or resume behavior.

Use migration status or dry-run tools and `EXPLAIN` where available. Use `EXPLAIN ANALYZE` only for safe read-only queries in an isolated or explicitly approved environment because it executes the statement. Do not run destructive SQL, production migrations, backup restoration, failover, or external side effects without specific authorization.

Treat a backup as usable only when the authorized operational owner has evidence of a successful representative restoration. Do not perform that restoration unless it is explicitly authorized and within delegated ownership.

## Hand off evidence

Return concise evidence to the Tech Lead and CTO:

```text
Scope: schema, data, engine/version, environment, and delegated paths
Compatibility: affected application versions and expand/migrate/switch/contract sequence
Changes: migrations, indexes, constraints, SQL, backfills, and Redis implications
Safety: authorization, data sensitivity, locks, runtime, stop conditions, and irreversible steps
Recovery: backup evidence, restoration evidence owner, rollback and roll-forward limits
Validation: exact command/environment -> result
Performance: representative plans, timings, contention, storage, and write impact
Residual risks: unavailable production-like evidence, operational owner, or untested failure paths
Outcome: blocked | changes-required | ready-for-review
```

Do not create a per-mission Markdown report or write ForgeOS centralized state. Critical, destructive, production, access-control, backup, restore, or irreversible changes require independent review and explicit human authorization; implementation completion is not self-approval.
