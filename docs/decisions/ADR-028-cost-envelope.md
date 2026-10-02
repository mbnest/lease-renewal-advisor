# ADR-028: Run a lean eval plan under a provisional $50 ceiling

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-006 (grading), ADR-007 (caching), ADR-012 (data scale), ADR-017 (model gateway) |
| **Pending** | DD-08 (cost ceiling and measured per-case cost) |

## Context

The project pays for every model call. A full pass with 3 runs for every configuration, plus ablations, means several thousand calls. Dev reruns are the main spend risk, and replay from cache costs nothing (ADR-007).

## Decision

**Repeat runs only where the headline comparison needs them, develop on a subset from cache, and cap spend in config.**

**Run plan**

- Published results: 3 runs for the baseline and for the full multi-agent configuration only.
- Per-agent score delta checkpoints and ablations: 1 run.
- Classifier ablation: scenario 5 homes only. Tool ablation: condition agent only (ADR-002).
- Dev: a 20-home subset, 1 run, replay from cache. The 60-home set is for published runs.

**Controls**

- Provisional $50 total ceiling, revisited after the bake-off (ADR-017).
- Per-run spend abort in config.
- Per-case token and step caps.
- Account-level spend limit on the gateway key.

**Estimates (assumptions, not measured)**

- Tokens per call: specialist 3k in and 0.6k out. Supervisor 2 turns of about 5k in and 0.8k out. Classifier 2k in and 0.2k out. Baseline 6k in and 0.9k out.
- At an assumed $0.30 input and $1.00 output per 1M tokens, the lean plan costs about $4.
- Reasoning models bill thinking tokens as output and can raise this.
- All estimates are replaced with measured token counts after the baseline run.

## Alternatives considered

- **3 runs for every configuration.** Rejected. Roughly doubles spend for comparisons that are not headline results.
- **Staged slices, with some specialists left as designed only.** Declined. Cheaper models make full scope affordable.
- **A local open model for dev.** Declined. It adds a second model seam, and prompts do not transfer.
- **Batch APIs and prompt caching.** Not assumed. They are provider features, not guaranteed through the gateway.

## Consequences

**Benefits**

- Full scope fits a small budget at expected prices.
- The spend abort stops a runaway run before it reaches the ceiling.

**Costs we accept**

- Single-run checkpoints and ablations carry no flip rate.
- Estimates rest on assumed prices and token counts until measured.

## Revisit when

- The spend ceiling is reached, or schema failures dominate results. Then reconsider staged slices.
- The bake-off shows measured cost per case far from the estimate (DD-08).

## Known gaps and open questions

- The ceiling is provisional until the bake-off and baseline run (DD-08).
- The account-level spend limit setting on the gateway is not verified.
