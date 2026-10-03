# ADR-008: Trace through the project's own decorator over MLflow

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-001 (orchestration), ADR-007 (caching), ADR-024 (redaction), ADR-025 (observability substitution) |
| **Pending** | DD-05 (MLflow version pin and span nesting check), DD-06 (Free Edition feasibility) |

## Context

Tracing should be in place from the start, and confirmed for each component as it is added, alongside its eval checkpoint.

- Agent code should not depend on a tracing vendor.
- Specialists run in parallel under `asyncio.gather`, and their spans must nest under the supervisor span.
- Protected fields must never reach a span or trace store.

## Decision

**A thin decorator, `@traced(kind, name)`, wraps MLflow. Agent code never imports MLflow.**

- It starts as a no-op stub. MLflow is swapped in behind it.
- **The decorator owns the trace attributes:** case id, run index, cache hit, token counts, schema validation result, and critic verdict.
- MLflow autolog is optional inside the wrapper for LLM spans. The cache layer emits its own span, tagged `cache_hit`.
- **Backend:** a local MLflow store in Docker, with a persistent volume and a UI container. From MLflow 3.7.0 the default backend is SQLite.
- Traces are tagged with grading outcome after the fact. Eval results are also logged as MLflow runs. Eval files stay the source of truth, and MLflow holds a copy.
- **Redaction boundary:** only post-redaction data reaches spans or trace storage ([ADR-024](ADR-024-substitution-redaction-and-key-isolation.md)).
- Tests: every registered agent and tool is traced, and parallel specialist spans nest under the supervisor.

## Alternatives considered

- **Call MLflow directly in agent code.** Rejected. It couples every agent to one vendor, and spreads attribute naming across the code.
- **A JSONL trace log only.** Rejected. No span tree, no UI, and no link to eval runs.

## Consequences

**Benefits**

- One place sets trace attributes and enforces the redaction boundary.
- Moving to managed MLflow ([ADR-025](ADR-025-substitution-observability.md)) changes the decorator, not the agents.

**Costs we accept**

- Local traces do not migrate to a managed workspace. Published run traces need export or snapshot artifacts.
- One more layer to maintain.

## Revisit when

- The Databricks layer is built and managed MLflow is available on the target workspace.
- The pinned MLflow version fails the span nesting check.

## Known gaps and open questions

- The exact MLflow version is not pinned yet ([DD-05](../open-decisions.md)).
- Managed MLflow availability on Free Edition is not confirmed ([DD-06](../open-decisions.md)).
