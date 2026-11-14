---
name: mobile-development
description: Implement and validate scoped Expo and React Native changes using the project's installed router, component system, styling engine, API contracts, and platform configuration. Use for mobile screens, components, hooks, services, offline behavior, and tests; do not use for uncoordinated backend, web, infrastructure, build, or store-release changes.
---

# Mobile development procedure

## Establish the implementation basis

1. Confirm the requested mobile behavior, acceptance criteria, target platforms and supported versions, device states, API dependencies, offline expectations, native capabilities, and delegated file ownership.
2. Inspect manifests and lockfiles, Expo and React Native versions, app and EAS configuration, Expo Router structure, dependencies and native modules, design-system components, NativeWind or Uniwind configuration, API and authentication clients, storage, notifications, linking, tests, and validation scripts.
3. Record the actual installed stack. Preserve its router, React Native Reusables components, styling engine, form and state tools, secure storage, persistence, notification, and test choices; do not infer them from ForgeOS profiles.
4. Identify existing screens, layouts, components, hooks, services, tokens, platform utilities, and test patterns before adding an abstraction. Follow application and framework naming conventions, not ForgeOS organization-file naming.

## Plan platform boundaries

Map each requirement to the smallest affected route, screen, component, hook, service, storage boundary, native configuration, and test. Define Android and iOS differences, safe-area and keyboard behavior, accessibility states, permission states, offline transitions, and failure recovery before coding.

Reuse React Native Reusables primitives and the configured design tokens where they fit. They are native project components, not web shadcn/ui; do not introduce DOM, CSS, Radix, or browser-only assumptions. Use NativeWind or Uniwind only when already configured, and never mix or migrate styling engines without approval.

Stop and coordinate before adding a dependency, native module, configuration plugin, permission, entitlement, schema or destructive local-data migration, API-contract change, backend or web change, infrastructure work, EAS build, production update, signing, or store submission.

## Implement the mobile flow

- Keep navigation and route parameters typed and validate all external links and notification payloads before routing.
- Build accessible components with platform-appropriate semantics, touch targets, focus, screen-reader labels, dynamic text, contrast, reduced motion, keyboard behavior, safe areas, gestures, loading, empty, error, denied-permission, offline, and retry states.
- Use existing API and authentication clients. Treat backend validation and authorization as authoritative; do not invent contract fields or weaken security in the client.
- Store sensitive tokens only in the installed platform-secure storage, such as SecureStore when appropriate. Never place them in AsyncStorage, SQLite, source, logs, links, notifications, screenshots, or fixtures.
- For SQLite or offline data, define ownership, transactions, migrations, cache bounds, synchronization state, conflict behavior, retries, idempotency, and recoverable partial failure. Do not promise offline writes the server cannot reconcile.
- Request native permissions only for approved features, at the point of need, with denial and restricted-state behavior. Keep notification payloads minimal and handle push-token rotation and logout.
- Avoid unnecessary renders, unvirtualized long lists, blocking JS work, oversized media, memory retention, wasteful network calls, and heavy startup paths. Optimize from profiler or structural evidence rather than habit.

## Test and validate

Add or update the smallest relevant tests with installed tools: unit tests for deterministic hooks and services, component tests for interactions and accessibility, integration tests for navigation and storage, and device or emulator checks for platform behavior, permissions, offline transitions, notifications, and deep links when authorized and available.

Run narrow tests first, then configured lint, type checks, broader suites, Expo diagnostics, and platform checks according to risk. Do not install tools, retrieve secrets, contact unauthorized production services, trigger EAS builds or submissions, or claim untested Android/iOS behavior. Record exact commands, exit codes, platforms, devices or simulators, results, skipped checks, and environment limitations.

## Hand off evidence

Return concise evidence to the Tech Lead and CTO:

```text
Scope: behavior, platforms, and delegated paths
Stack evidence: Expo/React Native versions, router, components, styling, native modules, and tests
Changes: routes, screens, components, hooks, services, storage, permissions, notifications, links, and tests
Contracts: API, authentication, offline, notification, and native-configuration assumptions
Validation: command/platform/device -> result
Quality: accessibility, safe areas, permissions, secure storage, offline, and performance checks
Residual risks: untested OS versions, devices, native paths, external services, or release steps
Outcome: blocked | changes-required | ready-for-review
```

Do not create a per-mission Markdown report or write ForgeOS centralized state. Critical authentication, storage, permission, native configuration, privacy, signing, or release changes require independent review; implementation completion is not self-approval.
