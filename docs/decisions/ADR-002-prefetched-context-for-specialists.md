# ADR-002: Prefetch specialist context in code

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-001 (orchestration), ADR-005 (tool access), ADR-007 (caching) |
| **Pending** | None |

## Context

Each specialist (condition, market, resident) reasons over one home's history: work orders, comps, payments, complaints, and messages. Per-lease history is small and fits in a model's context.

The data-access functions already exist behind the data-access interface, and can later be wrapped as tools ([ADR-005](ADR-005-custom-thin-mcp-server.md)).

Evaluation needs the same inputs on every run of a case, so that a change in score can be attributed to the agent and not to what it happened to fetch.

## Decision

**Code prefetches each specialist's context through the data-access functions before the specialist runs.** Specialists have no data tools in the first release.

- One optional ablation: the condition agent gets a single narrow `get_work_order_detail` tool, scored against prefetch on the same cases.

## Alternatives considered

- **Specialists fetch their own data through tools.** Not chosen. Tool calls add nondeterminism to the inputs, and a new failure mode: the agent never fetches the key record.
- **Hybrid: prefetch summaries and recent records, with bounded detail lookups as tools.** Deferred. It is the planned path if histories outgrow the context (see revisit).

## Consequences

**Benefits**

- Inputs are deterministic and cacheable ([ADR-007](ADR-007-one-cache-mechanism-two-lifecycle-points.md)).
- No tool-call loops inside specialists, so step counts stay fixed.

**Costs we accept**

- Input tokens are spent on context an agent may ignore.
- No cross-record drill-down on large histories.

## Revisit when

Move to the hybrid design when any of these hold:

- A domain's history exceeds a context budget, and truncation would drop evidence the decision needs.
- Cost per case is dominated by input tokens the agent mostly ignores.
- Cases need drill-down that summaries cannot support, such as multi-year vendor invoices.

The change is a wrapper over the existing access functions plus an eval re-baseline, not a redesign. Its costs to plan for: tool-call nondeterminism, caching of tool outputs, and measuring how often the key record is never fetched.

## Known gaps and open questions

- No context budget per domain is set yet.
