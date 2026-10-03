# ADR-022: Serve tools from a custom thin MCP server for release one, managed UC Functions MCP as the target

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-002 (prefetched context), ADR-005 (custom MCP server), ADR-011 (local-first release), ADR-021 (storage), ADR-024 (redaction) |
| **Pending** | DD-06 (Free Edition feasibility, including managed MCP) |

## Context

Tool access sits behind the same Python access functions that prefetch uses (ADR-002). ADR-005 sets the first-release server and why managed UC Functions MCP is the only managed option that keeps evidence deterministic. This record states the substitution itself.

## Decision

**Release one serves tools from a custom thin MCP server. The target is the managed Databricks MCP server for Unity Catalog functions. The tool contract is the seam.**

| | |
|---|---|
| Target | Managed MCP server for UC functions, with each access function registered as a UC function |
| Release one | Custom thin MCP server over the Python access functions, added after evals are measurable |
| Seam | Tool contract: tool names and Pydantic input and output schemas |

**Preserved by the stand-in**

- Tool names, arguments, and return schemas.
- Fixed, parameterized calls. No generated SQL.
- Redaction before any tool output leaves the data layer (ADR-024).

**Not preserved**

- UC permission checks on each call.
- On-behalf-of auth for the calling user.
- Hosting, scaling, and serverless compute pricing.

**Swap rule:** an equivalence test must show the same calls return the same evidence from both servers before agents use the managed one.

## Alternatives considered

- **Managed server from the start.** Not chosen for release one. It needs a workspace and redacted UC views or column masks (ADR-005, ADR-024).
- **Genie or Databricks SQL through managed MCP.** Rejected. Generated queries make evidence nondeterministic and break answer-key derivability (ADR-005).

## Consequences

**Benefits**

- Agents and eval code see one tool contract for both servers.
- The equivalence test turns the swap into a measured change.

**Costs we accept**

- UC functions must mirror the Python functions, so logic exists twice on the target until one is retired.

## Revisit when

- The Databricks backend is built (ADR-021). Register the functions in UC, run the equivalence test, and record the comparison here.

## Known gaps and open questions

- Managed MCP availability on Free Edition is not confirmed (DD-06).
- How UC functions reuse the Python access code, rather than reimplement it in SQL, is not decided.
