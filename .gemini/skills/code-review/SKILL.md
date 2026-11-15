---
name: code-review
description: Review code changes and diffs for correctness, security, regressions, performance, maintainability, test coverage, and project-convention violations. Use for initial or follow-up code reviews; do not use to implement fixes.
---

# Code review procedure

## Establish the review basis

1. Identify the requested scope, comparison base, intended behavior, and acceptance criteria. If the diff or base is unavailable, state the limitation before drawing conclusions.
2. Read the repository instructions and the relevant manifests, lockfiles, framework configuration, linting rules, and tests. Installed versions and established project conventions override generic preferences.
3. Inspect the full changed functions and their callers, consumers, data contracts, and tests when needed. A diff alone may hide a regression.

## Review by risk

Evaluate, in descending risk order:

- correctness and regression paths, including state transitions, errors, boundaries, concurrency, and compatibility;
- security controls, including authentication, authorization, validation, injection, secret handling, unsafe deserialization, and network or file access;
- data integrity and operations, including migrations, transactions, constraints, indexes, PostgreSQL query plans, Redis consistency, keys, eviction, and TTL behavior;
- performance, including N+1 queries, unnecessary network work, render or bundle regressions, mobile lifecycle costs, memory, and cache behavior;
- maintainability, framework-native conventions, public contracts, observability, and test adequacy.

Apply stack-specific semantics from the code actually present: Laravel/PHP, Next.js/React/TypeScript, Expo/React Native and React Native Reusables, Nuxt, NestJS, FastAPI, PostgreSQL, or Redis. Do not impose ForgeOS file-naming preferences on application code.

## Classify evidence

- `confirmed`: the inspected code, a reproducible path, or executed evidence directly demonstrates the defect.
- `potential`: a credible risk depends on a condition that has not been verified. Name that condition and how to verify it.

Do not report speculative style preferences. Report a convention or maintainability issue only when it has a concrete project impact.

## Assign severity

- `critical`: credible exploitation, catastrophic data loss, broad outage, or an immediate release blocker.
- `high`: likely serious security, correctness, data-integrity, or regression impact; blocks validation of a critical change.
- `medium`: meaningful but bounded defect or operational/maintenance risk that should be corrected.
- `low`: minor, actionable risk such as a localized convention, test, or maintainability gap.

## Write every finding

Use this structure and sort findings from highest to lowest severity:

```text
[severity] Short title
Classification: confirmed | potential
Location: path/to/file.ext:line or line range
Problem: what is wrong and the evidence supporting it
Impact: concrete user, security, data, performance, or maintenance consequence
Recommended correction: the smallest practical remediation
Verification: command, test, or inspection needed to prove the correction
```

Use exact current line numbers when available. Never invent a location; if generated code or missing context prevents precision, say so explicitly.

## Handle validation honestly

Run only authorized, non-destructive checks. Record exact commands and observed results. Clearly list relevant checks that were not run and why. A test suite passing does not erase a code-level finding, and an unexecuted test is not evidence.

## Re-review corrections

For each prior finding, inspect the new diff and relevant surrounding behavior. Re-run or request the smallest relevant validation. Mark a finding resolved only with code or execution evidence; otherwise keep it open and explain what remains. Report newly introduced issues separately.

## State the outcome

Use `blocked`, `changes-requested`, or `no-blocking-findings`. A critical change cannot receive `no-blocking-findings` while a `critical` or `high` observation is unresolved. Even `no-blocking-findings` does not replace GitHub branch protection, QA or security gates, or required human approval.

If there are no findings, say so directly and list residual risks, assumptions, and validation gaps.
