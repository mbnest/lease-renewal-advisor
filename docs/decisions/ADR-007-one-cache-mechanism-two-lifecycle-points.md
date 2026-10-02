# ADR-007: Use one cache for development and published results

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-008 (tracing), ADR-017 (model gateway), ADR-028 (cost envelope) |
| **Pending** | DD-02 (model and upstream provider selection) |

## Context

A full evaluation makes thousands of model calls. Development reruns the same cases many times, and published results must be reproducible by anyone later.

Under a gateway (ADR-017), the same model slug can be served by different upstream providers, at different prices and with different behavior.

## Decision

**One hash-keyed cache, used at two points in the lifecycle.**

- **Development.** A per-call cache. The key covers gateway, upstream provider, model slug, parameters, messages, and output schema. The run index is part of the key, so repeated runs stay independent samples.
- **Published results.** A frozen snapshot of the cache, with a manifest: model slug, upstream provider, price at run time, git commit, and data seed.
- **Replay fails loudly** on a cache miss. It never falls through to a live call.
- Replay still emits trace spans (ADR-008), tagged as cache hits.
- A change of model or upstream provider invalidates cached results.

## Alternatives considered

- **Separate dev cache and recorded-fixtures system.** Rejected. Two mechanisms drift apart, and published results would not use the code path tested in development.
- **No cache, rerun live.** Rejected. Costly, slow, and not reproducible.

## Consequences

**Benefits**

- Reruns from cache cost nothing, which keeps development within the cost envelope (ADR-028).
- Anyone can reproduce published scores from the snapshot, with no model access.

**Costs we accept**

- Strict keys mean a small prompt edit invalidates the cache and costs real calls.
- A snapshot pins results to a model that may later be retired.

## Revisit when

- A model slug or upstream provider is retired or changes behavior, so the snapshot no longer reproduces the live system.

## Known gaps and open questions

- Snapshot storage location and format are not chosen yet.
