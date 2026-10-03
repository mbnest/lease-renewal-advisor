# ADR-021: Store data in Parquet for release one, Delta in Unity Catalog as the target

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-002 (prefetched context), ADR-011 (local-first release), ADR-012 (tables), ADR-023 (data prep), ADR-024 (redaction) |
| **Pending** | None |

## Context

The core tables (homes, leases, payments, work orders, comps) are small, synthetic, and regenerated from a seed ([ADR-012](ADR-012-data-scale-scenarios-and-variants.md)). Release one runs locally ([ADR-011](ADR-011-databricks-target-local-first-release.md)). Agents and tools read data only through the data-access interface ([ADR-002](ADR-002-prefetched-context-for-specialists.md)).

## Decision

**Release one stores tables as Parquet files. The target is Delta tables in Unity Catalog. The data-access interface is the seam.**

| | |
|---|---|
| Target | Delta tables in Unity Catalog |
| Release one | Parquet files on a shared Docker volume |
| Seam | Data-access interface: function names, arguments, and Pydantic return types |

**Preserved by the stand-in**

- Table schemas and column types.
- Every read goes through the same access functions, so callers do not change.
- Deterministic reads for a given seed.

**Not preserved**

- UC governance: grants, lineage, audit of reads.
- Transactions and table versioning.
- Concurrent writers and scale.

## Alternatives considered

- **Delta in Unity Catalog from the start.** Not chosen for release one. It needs a workspace for every dev loop and every eval run (ADR-011).

## Consequences

**Benefits**

- No database to run. Files are versioned by seed and easy to inspect.
- The move to Delta changes one backend, not the callers.

**Costs we accept**

- Governance claims for storage stay unvalidated until the Databricks phase.

## Revisit when

- The Databricks phase starts (ADR-011). Load the same tables into Delta and run the same access-function tests against both backends.

## Known gaps and open questions

- Catalog and schema names on the target are not chosen.
