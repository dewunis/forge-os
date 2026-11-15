---
name: performance-audit
description: Measure, diagnose, optimize, and validate scoped application and data-path performance with reproducible before/after evidence. Use for profiling, benchmarks, load tests, Core Web Vitals, SQL, caching, concurrency, network, CPU, or memory work; do not use for unauthorized production load or speculative rewrites.
---

# Performance audit procedure

## Define the measurement contract

1. Confirm the user-visible or system outcome, target path, authorized environment, affected versions and components, ownership, expected workload, data sensitivity, and correctness constraints.
2. Define the metrics and acceptance thresholds before tuning. Select only relevant measures such as latency percentiles, throughput, error rate, Core Web Vitals, render or startup time, query count and duration, cache hit rate, event-loop or thread delay, CPU, memory, allocation, network bytes, battery, or saturation.
3. Record conditions needed for reproduction: commit or artifact, runtime and tool versions, hardware or device, dataset shape and scale, cache state, warm-up, concurrency, request mix, network conditions, duration, repetitions, and known background activity.
4. Confirm workload bounds, stop conditions, cleanup, monitoring, and data safety before execution. Never load-test production or modify production data, infrastructure, or runtime settings without explicit authorization for that exact target and action.

If representative measurement is unavailable, state why, keep conclusions as estimates or hypotheses, and define the smallest evidence needed to proceed. Do not manufacture a baseline.

## Establish a baseline

Run the narrowest representative scenario with tools already installed. Preserve raw results or existing project artifacts when permitted, and record the exact command, environment, exit code, duration, and relevant summary.

- Separate cold and warm behavior when caching, JIT, connection setup, bundles, or startup materially affect results.
- Use warm-up and multiple measured runs when practical. Prefer distributions and percentiles to averages for latency, and report errors alongside throughput.
- Keep workload, data, cache state, network, and resource limits controlled. Note variance and any run excluded for a documented technical reason; never discard an inconvenient result silently.
- Avoid observer effects where possible. Profiling and telemetry can change timings, so distinguish diagnostic runs from benchmark runs.

## Diagnose the bottleneck

Trace the measured path across the relevant boundaries and gather converging evidence before changing code:

- Browser and web UI: Lighthouse, Chrome DevTools, React Profiler, framework build output, Core Web Vitals, rendering, hydration, long tasks, bundles, images, and network waterfalls.
- Server applications: request traces, framework timing, Laravel Telescope when installed and safely configured, event-loop or worker behavior, serialization, I/O, queues, CPU, memory, and allocation profiles.
- Mobile: project-compatible Expo, React Native, Android, iOS, or Flipper tooling already installed; examine startup, JavaScript and UI threads, rendering, lists, images, memory, battery, and network behavior on the specified device and build mode.
- PostgreSQL and MySQL: query counts, N+1 behavior, safe execution plans, cardinality, indexes, locks, contention, connection pools, and data distribution. Use `EXPLAIN ANALYZE` only for safe read-only statements in an isolated or explicitly approved environment.
- Redis and caching: hit and miss behavior, TTL and invalidation, hot keys, serialization, round trips, pipelining, memory, eviction, stampedes, locks, and consistency requirements.
- Load and concurrency: bounded k6 or autocannon scenarios when already available, with explicit arrival pattern, concurrency, duration, thresholds, errors, saturation signals, and abort conditions.

Rank hypotheses by evidence, expected impact, risk, and cost. Identify the dominant constraint and distinguish correlation from causation.

## Make the smallest justified change

Tie each authorized change to a measured bottleneck and expected metric movement. Preserve observable behavior, security controls, accessibility, data integrity, cache semantics, framework conventions, and maintainability.

Prefer a bounded query, render, allocation, serialization, caching, batching, pagination, concurrency, or network improvement over a cross-system redesign. Account for transferred cost: faster reads can increase writes or memory; caching can add staleness and invalidation risk; concurrency can increase contention; smaller payloads can increase CPU; precomputation can increase storage and complexity.

Do not install tools or dependencies, change infrastructure or production settings, weaken controls, or expand into unrelated refactoring without approval and coordinated ownership.

## Validate before and after

Repeat the baseline scenario under conditions as equivalent as practical. Report both absolute and relative changes, run counts, variability, errors, and resource effects. Re-run relevant correctness, regression, concurrency, cache, and data-integrity checks before accepting a gain.

Classify the outcome accurately:

- `measured-improvement`: acceptance thresholds met with comparable evidence and no blocking regression.
- `measured-regression`: one or more relevant metrics or constraints worsened materially.
- `inconclusive`: variance, environment drift, missing data, or conflicting signals prevent a defensible comparison.
- `estimated-only`: no reliable before/after measurement was possible; all claimed effects remain projections.
- `blocked`: authorization, safety, tooling, correctness, or environment constraints prevent responsible execution.

Never relabel an estimate as a measured gain. A faster benchmark does not pass when correctness, security, accessibility, error rate, resource bounds, or operational safety fails.

## Hand off centralized evidence

Return a concise evidence block to the Tech Lead and CTO:

```text
Scope: target path, environment, versions, delegated files, and constraints
Contract: workload, dataset/cache state, metrics, thresholds, repetitions, and stop conditions
Baseline: exact command/tool -> observed distribution, errors, and resources
Diagnosis: evidence-backed bottleneck; hypotheses and confounders
Changes: authorized files and optimization rationale
After: equivalent command/tool -> observed distribution, errors, and resources
Comparison: absolute/relative measured effects; estimates clearly labeled
Validation: correctness/regression/concurrency/cache/data checks and results
Tradeoffs: security, maintainability, cost, capacity, consistency, accessibility, and operations
Residual risks: unavailable evidence or non-representative conditions
Outcome: measured-improvement | measured-regression | inconclusive | estimated-only | blocked
```

Do not create a per-mission Markdown report or write ForgeOS centralized state. Critical, production, data, infrastructure, security-sensitive, or architectural changes require independent review and the appropriate human authorization.
