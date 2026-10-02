# ADR-005: Start tool access with a thin custom MCP server

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-002 (prefetched context), ADR-011 (local-first release), ADR-022 (tool access substitution), ADR-024 (redaction) |
| **Pending** | DD-06 (Free Edition feasibility, including managed MCP) |

## Context

Data access sits behind Python functions. Tool names and their Pydantic schemas are the contract, so agent code does not depend on the backend.

- Redaction of protected fields lives in the data layer, for any server (ADR-024).
- Evaluation needs deterministic evidence, so every answer key can be derived from the data plus the policy.
- The first release runs locally (ADR-011).

## Decision

**A thin custom MCP server wraps the same Python access functions. It is added after evals are measurable.**

- Parquet backend first. A Databricks SQL backend is stubbed and documented.
- The target is the managed Databricks MCP server for Unity Catalog functions (ADR-022). It is the only managed option whose calls are fixed, parameterized, and deterministic.
- Any swap between servers is gated by an equivalence test: the same calls return the same evidence.

## Alternatives considered

- **Managed UC Functions MCP from the start.** Not chosen for the first release. It needs a Databricks workspace and redacted UC views or column masks. It is the target.
- **Genie or Databricks SQL free-form queries through managed MCP.** Rejected. Generated SQL makes evidence nondeterministic, which breaks answer-key derivability.
- **AI Search (vector search).** Not applicable. The data is structured records and short texts per home.

## Consequences

**Benefits**

- Runs locally and in Docker with no workspace.
- The same access functions serve prefetch (ADR-002) and the server, so there is one code path to test.

**Costs we accept**

- A server to write and maintain.
- The managed route needs redacted UC views or column masks to keep the redaction guarantee.

## Revisit when

- The Databricks backend is built. Register the same functions as UC functions, switch to the managed server, and record the comparison in ADR-022.

## Known gaps and open questions

- Managed MCP availability on Free Edition is not confirmed (DD-06).
- The managed server's release status needs confirming in the workspace. The older labs UC server is the one marked Beta and deprecated.
