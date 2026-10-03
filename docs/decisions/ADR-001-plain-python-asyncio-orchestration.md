# ADR-001: Orchestrate agents in plain Python with asyncio

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-003 (economics and critic stay code), ADR-007 (caching), ADR-008 (tracing), ADR-011 (local-first release), ADR-017 (model gateway), ADR-018 (arbitration) |
| **Pending** | None |

## Context

Each case runs the same fixed flow:

1. The condition, market, and resident specialists run in parallel.
2. Code arbitrates any conflict between their outputs ([ADR-018](ADR-018-fixed-arbitration-precedence.md)).
3. The supervisor synthesizes the outputs and the arbitration outcome, explains that outcome, and calls the economics function as a tool.
4. Code clamps the rent change and runs the critic.
5. A human approves or rejects later, in the gate, outside the flow.

There is no open-ended agent-to-agent chat, no dynamic planning, and no retry loop. Every agent returns schema-validated JSON, with steps and tokens capped per case and low temperature.

The orchestration layer has to support:

- **Parallel calls** with per-case step and token caps
- **Cache and replay** of every model call for evaluation ([ADR-007](ADR-007-one-cache-mechanism-two-lifecycle-points.md))
- **Tracing** through the project's own decorator ([ADR-008](ADR-008-mlflow-tracing-behind-own-decorator.md))
- **Running locally** in the first release ([ADR-011](ADR-011-databricks-target-local-first-release.md))

## Decision

**Orchestration is plain Python with asyncio and Pydantic contracts.** A thin model client handles calls and structured output only, through the single gateway in [ADR-017](ADR-017-one-gateway-tiered-models.md).

- Agent logic sits behind a thin interface, so a framework port stays possible. The project does not build for one.
- Orchestration is the same locally and on the Databricks target, so it has no substitution ADR.

## Alternatives considered

- **LangGraph.** Not chosen. Its strengths are durable state, long human pauses inside the graph, and complex branching. This flow has none of them, so the framework would add a dependency and an abstraction layer without using what it offers.
- **Databricks Agent Bricks (low-code orchestration).** Rejected. It cannot run in the local first release, and it puts control flow, caching, and tracing outside the code the evaluation depends on.

## Consequences

**Benefits**

- The control flow is explicit, readable, and tested like any other code.
- Cache, replay, and tracing wrap model calls directly, with no framework hooks in between.
- Fewer dependencies to pin and upgrade.

**Costs we accept**

- Timeouts, concurrency limits, and step and token caps are written and tested by hand.
- No built-in persistence, checkpointing, or graph visualization.

## Revisit when

- Durable state across runs, human pauses inside the flow, or complex branching become requirements.

## Known gaps and open questions

- The thin model client interface is not specified yet. Its shape follows from ADR-017 and the OpenRouter structured-output options.
