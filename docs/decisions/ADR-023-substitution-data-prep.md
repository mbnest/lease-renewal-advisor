# ADR-023: Prepare data with a seeded Python generator for release one, a Databricks pipeline as the target

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-011 (local-first release), ADR-012 (data scale), ADR-013 (ground truth and validator), ADR-021 (storage), ADR-024 (redaction and key isolation) |
| **Pending** | None |

## Context

The dataset is generated from a scenario spec and a seed (ADR-012). A generation-time validator checks every answer key against the evidence and fails generation on mismatch (ADR-013). LLM-written text is generated once and frozen as fixtures.

## Decision

**Release one prepares data with a seeded Python generator. The target is a declarative pipeline on Databricks. The generator output schema is the seam.**

| | |
|---|---|
| Target | Lakeflow Spark Declarative Pipelines writing Delta tables (ADR-021) |
| Release one | Seeded Python generator writing Parquet, followed by the validator |
| Seam | Generator output schema: core tables, answer keys, and frozen text fixtures |

**Preserved by the stand-in**

- Output tables and their schemas.
- Same seed, same data.
- Validator checks run before any table is published.
- Answer keys are written outside the agent-readable path (ADR-024).

**Not preserved**

- Pipeline orchestration, data quality expectations, and lineage on the platform.
- Incremental refresh and scale.

## Alternatives considered

- **Pipeline from the start.** Not chosen for release one. It needs a workspace for every regeneration, and the data is small.

## Consequences

**Benefits**

- Regeneration is one local command, cheap enough to run on every spec change.
- The validator runs in the same process as the generator, so a bad key stops generation.

**Costs we accept**

- Pipeline claims stay unvalidated until the Databricks phase.

## Revisit when

- The Databricks phase starts (ADR-011), or data volume outgrows a single local process.

## Known gaps and open questions

- Not decided: whether the target pipeline reruns generation on the platform, or ingests the generator's validated output.
- How validator checks map onto pipeline expectations is not designed.
