---
type: "manual"
---

Primary stack: Python 3.11, fast API.
Testing: pytest(coverage ≥ 85% on changed lines).

CI: GitHub Actions with required steps (lint, typecheck, test, build, audit).

Logging: e.g., pino JSON with {requestId, userId, spanId}.

Error model: AppError(code, httpStatus, cause).

Migration tool: Prisma Migrate / Liquibase / Flyway (review every DROP/ALTER COLUMN).

Observability: OpenTelemetry traces + Prometheus metrics + Sentry errors.

