# ADR-025: Trace to local MLflow for release one, Databricks-managed MLflow as the target

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-007 (caching), ADR-008 (tracing decorator), ADR-011 (local-first release), ADR-024 (redaction) |
| **Pending** | DD-05 (MLflow version pin and span nesting), DD-06 (Free Edition feasibility, including managed MLflow) |

## Context

Agent code traces only through the project's `@traced` decorator, and only the decorator imports MLflow ([ADR-008](ADR-008-mlflow-tracing-behind-own-decorator.md)). Eval results are logged as MLflow runs, while eval files stay the source of truth.

## Decision

**Release one traces to a local MLflow store in Docker. The target is Databricks-managed MLflow. The tracing decorator is the seam.**

| | |
|---|---|
| Target | Databricks-managed MLflow in the workspace |
| Release one | Local MLflow server and UI in Docker Compose, SQLite backend on a persistent volume |
| Seam | `@traced` decorator and the eval run logger |

**Preserved by the stand-in**

- Span tree, span kinds, and trace attributes set by the decorator.
- Eval runs with the same params and metrics.
- Only post-redaction data in spans ([ADR-024](ADR-024-substitution-redaction-and-key-isolation.md)).

**Not preserved**

- Workspace auth and permissions on experiments and traces.
- Managed storage, retention, and scale.

## Alternatives considered

- **Managed MLflow from the start.** Not chosen for release one. Every dev trace would need a workspace ([ADR-011](ADR-011-databricks-target-local-first-release.md)).

## Consequences

**Benefits**

- The swap is a tracking URI change behind the decorator.
- Local traces cost nothing and work offline.

**Costs we accept**

- Trace sharing is limited to whoever runs the local stack. Durable records are the eval files and snapshots ([ADR-007](ADR-007-one-cache-mechanism-two-lifecycle-points.md)).

## Revisit when

- The Databricks phase starts and managed MLflow is available in the target workspace ([DD-06](../open-decisions.md)).
- The pinned MLflow version fails the span nesting check ([DD-05](../open-decisions.md)).

## Known gaps and open questions

- MLflow version is not pinned (DD-05).
- Managed MLflow availability on Free Edition is not confirmed (DD-06).
