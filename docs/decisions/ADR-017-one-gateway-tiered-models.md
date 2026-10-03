# ADR-017: Route all model calls through one gateway, with tiered models

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-001 (orchestration), ADR-004 (critic classifier), ADR-007 (caching), ADR-011 (local-first release), ADR-028 (cost envelope) |
| **Pending** | DD-02 (model selection by bake-off), DD-08 (cost ceiling) |

## Context

A full evaluation makes thousands of model calls, and the project pays for every one. It must be affordable at full scope: baseline, three specialists, ablations, and repeat runs.

Tiering is chosen partly to keep the project manageable. A production deployment would test model fit per agent.

## Decision

**OpenRouter is the single gateway. Specialists use a smaller tier; the supervisor and the compliance classifier use a larger one.**

- Tier-to-agent assignment is a config choice, set after the baseline run.
- **Models are not named yet.** They are chosen by a baseline bake-off ([DD-02](../open-decisions.md)).
- **Hard gates:** structured outputs advertised, tool calling for the supervisor model, a pinnable model slug, a pinnable upstream provider.
- **Scored:** schema-valid rate, baseline action accuracy and flag recall, flip rate on a repeat run, cost per case, latency.
- **Bake-off:** baseline prompt only, 5 to 6 candidates, 35 homes (25 clean and 10 planted from the dev set), 1 run, about 200 calls. Repeat 2 candidates once for flip rate.
- **Free variants** are for dev smoke tests only, never published runs.
- **Reproducibility:** pin the model slug and upstream provider, and disable fallback routing. Record upstream provider and price at run time in the cache key and snapshot manifest ([ADR-007](ADR-007-one-cache-mechanism-two-lifecycle-points.md)).

## Alternatives considered

- **One model vendor's API direct.** Rejected. Locks the project to one vendor's prices and model range before any bake-off.
- **Databricks model serving.** Not chosen. Release one is local ([ADR-011](ADR-011-databricks-target-local-first-release.md)). Kept as an optional seam, off the critical path.
- **One model for every agent.** Rejected. Specialists do narrow extraction and do not need the larger tier's cost.

## Consequences

**Benefits**

- One client, one key, and many models to compare on the same harness.
- Cheaper models make the full scope affordable.

**Costs we accept**

- Routing can change upstream behavior silently. Pinning reduces this but must be verified.
- Schema and tool-call reliability vary by model and endpoint. Weaker models may lower absolute scores.
- An LLM message judge may share a model family with a graded agent and favor its output.

## Revisit when

- Schema failures dominate bake-off or eval results.
- Routing nondeterminism breaks reproducibility despite pinning.
- Databricks model serving becomes viable in the Databricks phase ([DD-06](../open-decisions.md)).

## Known gaps and open questions

- Exact request options for provider pinning and fallback disabling are not verified in the OpenRouter docs yet (DD-02).
- Candidate prices are snapshots and must be rechecked before the bake-off.
