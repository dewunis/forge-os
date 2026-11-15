---
name: software-testing
description: Plan, implement, execute, and report software tests with reproducible evidence. Use for unit, integration, functional, end-to-end, regression, or bug-fix validation; do not use to alter business code or claim unexecuted results.
---

# Software testing procedure

## Establish the test basis

1. Identify the requested behavior, confirmed acceptance criteria, affected paths, risk, supported platforms, and comparison baseline. Separate confirmed requirements from assumptions and open questions.
2. Read repository instructions, manifests, lockfiles, test configuration, existing tests, CI commands, and relevant implementation code. Use the project's installed framework, versions, conventions, helpers, and commands.
3. Map each acceptance criterion or material risk to at least one proposed check. Include normal, boundary, negative, failure, authorization, concurrency, accessibility, and platform cases only where relevant.
4. Record tests that are outside scope or impossible in the current environment instead of silently omitting them.

## Protect isolation and production data

Before running a command that can write data, verify the test environment and datastore target from effective configuration. Use disposable databases, transactions, fakes, mocks, temporary files, local emulators, or isolated test accounts as appropriate.

Stop and escalate when production separation is uncertain. Never migrate, reset, seed, truncate, or otherwise mutate production data. Do not expose secrets in commands, logs, fixtures, screenshots, or reports.

Keep tests independent of execution order and shared mutable state. Clean up owned data, processes, browsers, emulators, timers, and temporary files even after failure.

## Choose the smallest useful test layer

- Unit tests isolate deterministic rules and components.
- Integration tests verify collaboration with databases, framework services, queues, caches, APIs, or modules.
- Functional tests verify behavior through a public application boundary such as HTTP, UI, command, or job execution.
- End-to-end tests cover a small number of critical user journeys across real integrated boundaries.
- Regression tests reproduce a confirmed defect and remain after the correction to prevent recurrence.

Prefer lower-cost layers when they provide the same confidence. Do not duplicate the same assertion across every layer without a specific risk reason.

## Use the installed stack

Inspect project scripts and documentation before selecting exact commands:

- Laravel: use the configured Pest or PHPUnit runner for unit, HTTP, database, queue, event, and authorization behavior.
- Next.js and React: use configured Vitest and Testing Library suites for modules and components; use Playwright for browser-critical flows.
- Expo and React Native: use configured Jest and React Native Testing Library suites; use Maestro for device journeys when installed and available.
- Nuxt: use Vitest and the Nuxt/Vue-compatible utilities already configured by the project.
- NestJS: use Jest and Supertest for providers, modules, controllers, guards, pipes, and HTTP behavior.
- FastAPI: use pytest and HTTPX with safe dependency overrides and isolated async/database resources.

Do not install, upgrade, or substitute a test tool solely because it appears in this list. If the necessary tool is absent, report the gap and propose the smallest compatible option for approval.

## Implement maintainable tests

Test observable behavior rather than private implementation details. Use descriptive native naming, arrange setup clearly, keep assertions focused, and reuse project fixtures or helpers without hiding material behavior.

Create or modify only authorized test files and test-only support. Do not change business code, weaken assertions, add unconditional skips, or mock away the behavior under test to obtain a pass.

For a bug fix, capture the original failure when a safe baseline exists. After developers correct the product code, execute the regression test again and then the relevant surrounding suite.

## Execute and collect evidence

Run the narrowest relevant command first. Expand to related suites, type checks, builds, browsers, devices, or full regression only when required by risk and available resources.

For every command record:

- exact command and working directory;
- relevant environment or platform, without secrets;
- exit code and observed summary;
- counts of passed, failed, skipped, and other runner-specific outcomes;
- artifact paths such as traces, screenshots, videos, coverage, or logs when generated;
- duration or timeout when it affects reproducibility.

Preserve the first failure. A retry is additional evidence, not a replacement for it.

## Classify every planned test

- `passed`: executed and observed successful.
- `failed`: executed and observed unsuccessful, including setup or infrastructure failure; distinguish product failure from environment failure.
- `skipped`: the runner explicitly skipped, ignored, quarantined, or marked pending the test. Never count it as passed.
- `not-executed`: planned or relevant but not run; state the reason.
- `flaky`: outcomes differed across equivalent runs or depend on uncontrolled timing/state. Report every observed outcome and attempt count.

Coverage is supporting evidence only. Explain which risks and behaviors are asserted; do not use a percentage as proof of quality.

## Report results

Use a compact evidence summary:

```text
Scope: feature, criteria, platforms, and assumptions
Changes: test files or fixtures created/modified
Executed: command -> exit code -> passed/failed/skipped counts
Failures: reproducible steps, expected vs actual, and evidence/artifacts
Flaky: test, observed outcomes, attempts, and suspected dependency
Not executed: check and reason
Residual risks: untested paths or environment limitations
Outcome: blocked | failed | passed-with-gaps | passed
```

Use `passed` only when all required checks actually executed successfully and no blocking gap remains. Use `passed-with-gaps` when executed checks passed but disclosed non-blocking checks remain unexecuted. A critical regression or unresolved critical environment ambiguity makes the affected feature `blocked`.

Critical test changes require independent review. A QA result does not replace Code Review, Security review, protected branches, or required human approval.
