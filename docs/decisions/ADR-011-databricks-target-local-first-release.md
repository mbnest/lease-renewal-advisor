# ADR-011: Design for a Databricks target, release locally first

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-001 (orchestration), ADR-005 (custom MCP server), ADR-007 (caching), ADR-009 (UI and state), ADR-021 to ADR-027 (substitutions) |
| **Pending** | DD-06 (Free Edition feasibility) |

## Context

The intended home for the system is a governed data platform: catalog permissions, column masks, managed tracing, and a hosted app. The first release must still run without a paid or hosted workspace, and evaluation must be cheap and reproducible.

The target environment is Databricks Free Edition. Its limits shape what can run there:

- Serverless compute only, with a fair-usage quota. Exceeding it shuts compute down for the day, or in extreme cases the month.
- Non-commercial use, no SLA, and inactive accounts may be deleted.
- Published limits conflict across doc versions (app count, Lakebase support). They must be checked in a real workspace.

## Decision

**Architecture docs describe the Databricks target. Release one is local, and every local component is a documented substitution behind a seam.**

| Concern | Target | Release one | ADR |
|---|---|---|---|
| Storage | Delta in Unity Catalog | Parquet | ADR-021 |
| Tool access | Managed UC Functions MCP | Custom thin MCP server | ADR-022 |
| Data prep | Pipeline on Databricks | Seeded Python generator | ADR-023 |
| Redaction and answer-key isolation | UC views or column masks, restricted key schema | Python access layer, directory allowlist | ADR-024 |
| Observability | Databricks-managed MLflow | Local MLflow | ADR-025 |
| Approval and audit state | Lakebase | SQLite | ADR-026 |
| Reviewer UI | Streamlit as a Databricks App | Streamlit in Docker Compose | ADR-027 |
| Orchestration | Hand-coded asyncio | Same | ADR-001 |

- **Fidelity rule:** target components are marked "designed, not validated" in the README status table. Each substitution ADR states what the stand-in does not preserve: UC governance, on-behalf-of auth, concurrency, scale.
- **Packaging:** Docker Compose with app, MLflow, and eval runner services on shared volumes. SQLite is single-user.
- **Evals stay local** with cached replay (ADR-007). A live Free Edition app can be deleted or shut down by quota, so the durable record is the repo, the ADRs, frozen eval snapshots, and recorded demos.
- **Timing:** the Databricks phase starts after the local release is complete and documented.

## Alternatives considered

- **Build on Databricks first.** Rejected. Quotas and account deletion make it a fragile base for repeatable evals, and every dev loop would depend on a hosted workspace.
- **Local only, no target.** Rejected. Governance needs (redaction in the catalog, answer keys in a restricted schema) belong in the design even before they are built.

## Consequences

**Benefits**

- The first release runs anywhere with Docker and costs nothing to host.
- Each seam is named, so the migration path is explicit per component.

**Costs we accept**

- Target claims stay unvalidated until the Databricks phase.
- Free Edition quotas limit on-platform eval runs.

## Revisit when

- A seam flaw is suspected before the Databricks phase. The identical-redaction test (ADR-024) is the first seam to validate.

## Known gaps and open questions

- Free Edition limits for apps, Lakebase, managed MCP, managed MLflow, and quota are not confirmed (DD-06).
- Substitution ADRs ADR-021 to ADR-027 are planned, not written.
