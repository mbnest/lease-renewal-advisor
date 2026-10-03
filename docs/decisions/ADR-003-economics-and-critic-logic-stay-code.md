# ADR-003: Keep economics and critic logic in code

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-001 (orchestration), ADR-004 (critic design), ADR-020 (rent clamp) |
| **Pending** | None |

## Context

The full design names six roles: supervisor, condition, market, resident, economics, and critic. Agents are for judgment over unstructured input, not for logic that can be written down.

- The economics comparison, turnover cost against the renewal increase, is arithmetic over structured inputs.
- Claim verification needs checkable record ids and values, not an opinion.

## Decision

**LLM agents are limited to the supervisor and the three specialists (condition, market, resident).**

- **Economics is a code function** that the supervisor calls as a tool. It is the one tool-calling loop in the system.
- **The critic is code**, plus one narrow classifier for compliance ([ADR-004](ADR-004-critic-design.md)).

## Alternatives considered

- **Economics as an LLM agent.** Rejected. The comparison is arithmetic. A model adds cost and nondeterminism with nothing to judge.
- **A fully LLM critic.** Rejected. Claim checks against record ids and values are exact in code, and a model check would be neither cheaper nor more reliable.

## Consequences

**Benefits**

- Deterministic, unit-testable, and cheap.
- Economics and claim checks give the same answer on every run, so eval variance comes only from the agents.

**Costs we accept**

- Code cannot reason over unstructured vendor notes or lease addenda, if those inputs are added later.

## Revisit when

Promote economics or the critic to an agent only when all three hold:

- **Rule insufficiency.** Held-out cases show the code failing, clustered in inputs rules cannot express.
- **Measured lift.** The agent beats the code version on the eval set by a margin agreed in advance, with no increase in compliance misses or unsupported claims.
- **Acceptable controls.** Cost, latency, and nondeterminism stay within budget. Output is schema-validated and auditable. The code version stays as a fallback.

## Known gaps and open questions

- None
