# Supported stack catalog (planned skills)

- Backend: Laravel/PHP (primary), NestJS/TypeScript (optional), FastAPI/Python (optional).
- Web: Next.js/React/TypeScript + Tailwind CSS + shadcn/ui (primary); Nuxt/Vue (alternative); Laravel + Inertia (alternative).
- Mobile: Expo + React Native + TypeScript + Expo Router + React Native Reusables + NativeWind (preferred when compatible).
- Data: PostgreSQL (primary), MySQL/MariaDB (compatible), Redis, SQLite for local mobile storage, pgvector where justified.
- Testing: Pest/PHPUnit, Vitest, Playwright, Jest, Maestro (select according to project).
- Ops: Docker, GitHub Actions, Linux, Nginx/Caddy; cloud provider selected per project.
- Observability: Sentry; Prometheus/Grafana when justified.
- AI: OpenAI SDK, retrieval/RAG and vector stores only when needed.

These are **capabilities to support**, not installed tools. Stack profile selection must respect existing dependency versions and avoid automatic migrations/upgrades. React Native Reusables is not interchangeable with web shadcn/ui; apply platform-specific accessibility and interaction rules.
