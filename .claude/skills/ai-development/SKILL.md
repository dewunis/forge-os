---
name: ai-development
description: Design, implement, and evaluate scoped AI integrations with validated inputs and outputs, controlled data access, measurable quality, and bounded cost. Use for OpenAI Responses API, Agents SDK, Google Gemini API, Interactions API, Google GenAI SDK, embeddings, RAG, vector search, tools, structured outputs, or streaming; do not use for unauthorized data transfer, secret exposure, or large paid runs.
---

# AI development procedure

## Establish the integration basis

1. Confirm the user outcome, acceptance criteria, authorized data, provider, budget and run cap, latency target, quality and safety thresholds, affected applications, and delegated file ownership.
2. Inspect manifests and lockfiles, installed SDK versions, current provider clients, prompts, model settings, API and output contracts, tools, retrieval stores, data classifications, evaluation fixtures, observability, tests, and deployment boundaries.
3. Verify current official documentation for every provider feature, model, parameter, event, quota, pricing assumption, or SDK behavior that may have changed. Record the verified source and date in the implementation evidence, not in a new per-mission report.
4. Stop if authorization for private data, external transfer, paid usage, consequential tools, production access, or ownership is ambiguous. Never retrieve or expose secret values.

## Choose the simplest sufficient design

Start with deterministic code or one model call. Add retrieval only when external knowledge or corpus grounding is required; add tools only when the model must request bounded application capabilities; add the Agents SDK or multiple agents only when real orchestration, state, specialization, or handoffs justify the added failure, latency, security, and cost surface.

Prefer the Responses API for a new OpenAI integration when it fits current official guidance and project constraints. For a new Google Gemini integration, prefer the Interactions API (`client.interactions.create`) with the official `google-genai` (Python) or `@google/genai` (TypeScript/JavaScript) SDK when it fits current official guidance, avoid deprecated `google-generativeai` / `@google/generative-ai` SDKs and deprecated `gemini-1.5-*` / `gemini-2.0-*` / `gemini-2.5-*` models, and use the Gemini Live API only when real-time bidirectional streaming is required. Do not rewrite a working integration merely for API novelty.

Choose a model using current availability and evidence for capability, modality, structured outputs, tools, context, latency, reliability, and budget. Baseline the smallest suitable model and escalate only when evaluations justify it. Do not invent performance or cost claims.

## Define trust and data boundaries

- Classify each input, retrieved document, metadata field, prompt segment, model output, tool argument, and destination as trusted or untrusted.
- Minimize context and external data transfer. Preserve tenant isolation, authorization, provenance, deletion and retention rules, and prevent private data from entering prompts, logs, traces, caches, embeddings, or providers without approval. Explicitly disable provider-side storage defaults (such as setting `store=False` / `store: false` on Gemini Interactions API calls) whenever tenant, privacy, or retention policy prohibits provider-side state storage.
- Treat retrieved content and model output as untrusted data, never as higher-priority instructions. Delimit content, detect or contain prompt injection, allowlist sources and tools, and enforce permissions and side-effect approval in deterministic application code.
- Keep provider secrets server-side. Frontend and mobile applications call an authorized backend and never receive a secret provider key.

## Implement reliable behavior

- Validate inputs before the provider call and validate structured or free-form outputs before rendering, storing, executing, or using them in decisions.
- Give tools narrow schemas, least privilege, timeouts, idempotency, bounded results, application-side authorization, and confirmation for consequential effects.
- Bound retries by retryable error class, attempt count, deadline, jitter, idempotency, and cost. Handle rate limits, cancellation, partial streams, provider errors, safety refusals, empty results, malformed outputs, and degraded fallbacks explicitly.
- For RAG, version ingestion and embeddings, define chunking and metadata, tenant filters, retrieval limits, freshness and deletion, citations or provenance, and evaluate retrieval separately from generation. Coordinate vector schema and lifecycle with the Database Engineer.
- Instrument redacted request correlation, model and prompt version, latency, usage, estimated or measured cost, retrieval and tool outcomes, and error categories according to approved retention. Do not log secrets or sensitive content.

Follow native framework boundaries: server-side services or jobs for Laravel, server-only routes or services for Next.js, backend-mediated provider calls for Expo, and installed typed async patterns for FastAPI. Stop before modifying business logic, API contracts, databases, client interfaces, infrastructure, dependencies, ForgeOS agent models, global permissions, or technology profiles without explicit ownership and approval.

## Evaluate before claiming readiness

Create or reuse a versioned evaluation set covering representative tasks, boundary inputs, malformed outputs, refusals, prompt injection, retrieval misses, tenant isolation, tool authorization, rate limits, retries, streaming interruption, and failure fallbacks according to risk.

Define metrics and thresholds before execution. Record dataset version, prompt and model identifiers, parameters, environment, repetitions, grader method, raw counts, latency, token usage, and cost source. Separate deterministic assertions, human review, model-graded results, estimates, and unexecuted plans. Never present a mock result as provider quality evidence.

Run local and mocked checks first. Any external paid evaluation, embedding job, ingestion, or inference batch must be explicitly authorized and capped. Stop at the cap or on unexpected data, cost, safety, or error behavior.

## Hand off evidence

Return concise evidence to the Tech Lead and CTO:

```text
Scope: behavior, provider, authorized data, applications, and delegated paths
Docs and stack: verified sources/date, SDK, APIs, models, and installed tools
Design: simple-call/RAG/tools/agent rationale and trust boundaries
Changes: prompts, context, retrieval, tools, outputs, streaming, errors, and tests
Evaluation: dataset/version, command, model, measured results, latency, tokens, and cost
Security and privacy: data flow, injection controls, secrets, authorization, and retention
Residual risks: external calls not run, untested volume, model drift, provider limits, or cost uncertainty
Outcome: blocked | changes-required | ready-for-review
```

Do not create a per-mission Markdown report or write ForgeOS centralized state. Critical AI, privacy, security, consequential-tool, model-strategy, or high-cost changes require independent review; implementation completion is not self-approval.
