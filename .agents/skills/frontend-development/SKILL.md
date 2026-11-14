---
name: frontend-development
description: Implement and validate scoped web frontend changes using the project's installed framework, design system, API contracts, and conventions. Use for Next.js, React, TypeScript, Tailwind, shadcn/ui, Nuxt, or Vue interface work; do not use for uncoordinated backend, mobile, or infrastructure changes.
---

# Frontend development procedure

## Establish the implementation basis

1. Confirm the requested behavior, acceptance criteria, supported routes, devices and browsers, content states, API dependencies, and delegated file ownership.
2. Inspect manifests and lockfiles, framework and TypeScript configuration, router and source layout, styling and design tokens, existing components, API clients, authentication integration, tests, linting, and build scripts.
3. Record the actual framework and versions. Use the installed router, rendering model, component library, form tools, state tools, and test stack; do not infer them from ForgeOS profiles.
4. Identify reusable project primitives before creating a component. Follow native framework and application naming conventions, not ForgeOS organization-file naming.

## Plan boundaries before code

Map each requirement to the smallest affected page, layout, component, hook, schema, client, and test. Keep server data, URL state, local interaction state, and shared client state in the narrowest appropriate owner.

For Next.js App Router, decide Server versus Client Components deliberately. Start server-side and add a client boundary only for browser APIs, event handlers, client state, or installed client-only libraries. Choose SSR, SSG, caching, revalidation, streaming, and Suspense behavior from the data's freshness and user experience requirements, not habit.

For Nuxt or Vue, use the installed rendering mode, routing, Composition API, composables, and state conventions. Do not translate React patterns mechanically.

Stop and coordinate before changing an API contract, router architecture, shared state architecture, design system, dependency set, backend, migration, infrastructure, or mobile application.

## Implement the interface

- Compose existing design-system components and tokens before adding variants or primitives.
- Keep props, emits, loaders, actions, API responses, and error states typed. Narrow unknown external data instead of asserting it away.
- Provide semantic structure, labels, descriptions, keyboard operation, visible focus, appropriate announcements, useful errors, sufficient contrast, reduced-motion behavior, and logical focus movement.
- Design responsive behavior from content constraints and existing breakpoints. Verify narrow, intermediate, and wide layouts without encoding device-specific assumptions.
- Implement empty, loading, pending, success, partial, error, unauthorized, and not-found states that are relevant to the flow.
- Keep client validation consistent with server rules while treating server validation as authoritative.
- Never expose secrets or import server-only modules into client code. Treat UI authorization as presentation only and preserve backend enforcement.

Avoid wrappers, hooks, contexts, stores, variants, or generic components until a concrete reuse or lifecycle need exists. Do not duplicate an existing component merely to simplify a local edit.

## Integrate data and authentication

Use existing API clients, shared types, error mapping, cache strategy, and authentication/session patterns. Preserve request cancellation, race handling, retry behavior, and stale-data semantics where relevant.

Do not invent response fields, silently swallow contract errors, store privileged credentials in browser storage, or bypass backend authorization. Coordinate contract gaps through the Tech Lead and Software Architect.

## Protect performance

Check for unnecessary Client Components, hydration work, serial waterfalls, oversized imports, duplicate fetching, unstable keys, unbounded lists, layout shifts, unoptimized media or fonts, and avoidable rerenders.

Optimize from evidence and framework-native capabilities. Do not add memoization, lazy loading, caching, or state libraries without a measured or structurally clear benefit. State which Core Web Vitals risks were inspected; do not claim improvements without measurement.

## Test and validate

Add or update the smallest relevant frontend tests using the installed tools:

- unit tests for deterministic utilities and state transitions;
- component tests for rendering, interaction, forms, errors, semantics, and keyboard behavior;
- browser tests for critical routing, authentication presentation, responsive flows, and integrated user journeys;
- accessibility checks for automated rules plus manual keyboard, focus, naming, and announcement behavior where risk warrants it.

Run the narrowest relevant tests first, then configured lint, type-check, build, or broader browser checks according to scope and risk. Coordinate independent regression and cross-browser coverage with QA. Record exact commands, exit codes, results, skipped checks, artifacts, and environment limitations.

## Hand off evidence

Return a concise summary to the Tech Lead and CTO:

```text
Scope: behavior and delegated paths
Stack evidence: framework, router, versions, design system, and test tools
Changes: pages, components, state, forms, API integration, and tests
Validation: command -> result
Accessibility: checks performed and remaining gaps
Performance: inspected risks and measured evidence, if any
Contracts: API, authentication, or architecture assumptions
Residual risks: untested browsers, devices, states, or dependencies
Outcome: blocked | changes-required | ready-for-review
```

Do not create a per-mission Markdown report or write ForgeOS centralized state. Critical or security-sensitive changes require independent review; implementation completion is not self-approval.
