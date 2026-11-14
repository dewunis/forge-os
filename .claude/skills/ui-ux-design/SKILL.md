---
name: ui-ux-design
description: Design and validate scoped web or mobile user experiences from existing product goals, journeys, components, tokens, and platform conventions. Use for information architecture, user flows, textual wireframes, component and state specifications, responsive behavior, accessibility requirements, and design-system evolution; do not use for unsupported research claims or unrequested application implementation.
---

# UI/UX Design

## Establish the design context

Confirm the users, task, business outcome, scope, acceptance criteria, target platforms, risk, and available evidence. Inspect existing journeys, screens, components, styles, tokens, content, responsive behavior, accessibility patterns, and relevant framework configuration before proposing changes.

Separate observed evidence, confirmed requirements, assumptions, and hypotheses. Do not represent an expert review as user research or invent test results.

## Model the experience

Describe the current and intended journey, information hierarchy, navigation, decision points, and recovery paths. Resolve consequential product ambiguity with the Product Manager and structural constraints with the Software Architect before detailing the interface.

Prefer the smallest change that satisfies the outcome. Reuse the established design system and installed components; propose a new token, variant, or primitive only when an evidenced gap cannot be solved coherently with what exists.

## Specify the interface

Provide only the artifacts needed for implementation:

- a concise user flow or textual wireframe;
- content hierarchy and interaction behavior;
- mapping to existing web or mobile components;
- relevant empty, loading, pending, success, validation, error, unauthorized, offline, and recovery states;
- responsive and platform-specific adaptations;
- accessibility requirements and observable acceptance criteria;
- interface contracts, assumptions, and unresolved decisions.

Keep web shadcn/ui and mobile React Native Reusables mappings distinct. Follow the installed styling engine and native framework conventions.

## Validate proportionately

Review task completion, consistency, error prevention and recovery, content clarity, responsive reflow, input modalities, keyboard or switch operation, focus behavior, accessible naming, contrast, text scaling, reduced motion, screen-reader expectations, touch targets, safe areas, and Android or iOS conventions as applicable.

Use available non-destructive inspection or accessibility tools when authorized. Record what was inspected, the environment, actual results, limitations, and proposed follow-up. Never claim WCAG conformance, usability success, or performance improvement without supporting evidence.

## Hand off centrally

Return the scope, evidence, flow, component and token decisions, states, accessibility criteria, validation performed, assumptions, open questions, and implementation risks to the Tech Lead and CTO. Coordinate independent validation with QA and implementation review with the Code Reviewer.

Do not create a per-mission Markdown report or write ForgeOS centralized state. Do not modify application code unless that implementation and its file ownership were explicitly delegated.
