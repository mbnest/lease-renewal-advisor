# Risks

Status: decided, not specified or built. Last updated 2026-10-03.
What could make the results wrong, unreproducible, too costly, or misused, and how the design mitigates each. Every mitigation here is decided, not built or tested. Decisions live in the linked ADRs and the [deferred decisions register](open-decisions.md). This doc does not add new ones.

## How to read this
Every risk has the same four fields. A field with no decision behind it says "not decided" and points to the known gaps below.
- **Risk:** what can go wrong and why it matters
- **Mitigation:** what lowers the chance or the impact, before it happens
- **Detection:** the signal that shows it is happening
- **If it happens:** the response already decided, usually an ADR revisit trigger

Likelihood and impact are not rated. No rating rubric exists yet.

## Summary

| Risk | Area | Main mitigation | Owner | Open item |
|---|---|---|---|---|
| Routing nondeterminism | Models | Pin slug and upstream provider, no fallback | [ADR-017](decisions/ADR-017-one-gateway-tiered-models.md), [ADR-007](decisions/ADR-007-one-cache-mechanism-two-lifecycle-points.md) | [DD-02](open-decisions.md) |
| Run-to-run variation | Models | Low temperature, 3-run majority, flip rate | [eval plan](eval-plan.md#comparison-and-consistency) | None |
| Cheap-model schema failures | Models | Structured-output gate, schema-valid rate ranked first | [ADR-017](decisions/ADR-017-one-gateway-tiered-models.md) | DD-02, runtime handling |
| Model retirement | Models | Frozen snapshot with manifest | [ADR-007](decisions/ADR-007-one-cache-mechanism-two-lifecycle-points.md) | None |
| Price snapshot staleness | Cost | Price recorded per run, recheck before bake-off | [ADR-028](decisions/ADR-028-cost-envelope.md) | [DD-08](open-decisions.md) |
| Spend overrun | Cost | Ceiling, per-run abort, per-case caps | [ADR-028](decisions/ADR-028-cost-envelope.md) | DD-08 |
| Judge self-preference | Eval | No model grades a case | [ADR-006](decisions/ADR-006-evaluation-grading-rules.md) | Judge deferred |
| Small samples and leakage | Eval | Counts not percentages, held-out dev set, threshold freeze | [eval plan](eval-plan.md), [ADR-019](decisions/ADR-019-promotion-criteria-and-threshold-freeze.md) | [DD-03](open-decisions.md) |
| Rent pricing misuse | Domain | Advisory only, human approval, global clamp | [ADR-010](decisions/ADR-010-guardrails-tiering-and-audit-record.md), [ADR-020](decisions/ADR-020-rent-clamp-and-symbolic-bands.md) | None |
| Protected characteristics reach a decision | Domain | Redaction in the data layer, critic | [ADR-024](decisions/ADR-024-substitution-redaction-and-key-isolation.md), [ADR-004](decisions/ADR-004-critic-design.md) | None |
| Outputs read as legal advice | Domain | Narrow claims, advisory only | This doc | None |
| Synthetic data limits | Data | Results scoped to known planted cases | [ADR-012](decisions/ADR-012-data-scale-scenarios-and-variants.md), [ADR-013](decisions/ADR-013-ground-truth-and-compliance-trap.md) | [DD-01](open-decisions.md) |

## Models and gateway

### Routing nondeterminism
- **Risk:** the gateway (OpenRouter, one entry point to many model providers) can serve one model slug from different upstream providers. Price and behavior differ by provider, so a rerun may not reproduce a result
- **Mitigation:** pin the model slug and the upstream provider, and disable fallback routing. Record the upstream provider and price in every cache key and in the snapshot manifest. Published runs replay from a frozen snapshot that fails loudly on a cache miss
- **Detection:** a recorded provider that differs from the pinned one. Flip rate rising on a repeat run with an unchanged prompt
- **If it happens:** a provider change invalidates cached results, which are rerun. If pinning still fails to hold, revisit the gateway choice ([ADR-017](decisions/ADR-017-one-gateway-tiered-models.md#revisit-when)). Pinning options are not verified yet (DD-02)

### Run-to-run variation
- **Risk:** sampling makes the same case score differently across runs, so a single run can over- or understate quality
- **Mitigation:** low temperature on every agent. Headline configs (baseline and full multi-agent) run 3 times and score a 2-of-3 majority per case and per count
- **Detection:** flip rate, reported beside the scores. Single-run checkpoints and ablations have none
- **If it happens:** a count with no majority scores as a fail. Flipped cases are reported by count. Single-run deltas are read as directional only

### Cheap-model schema failures
- **Risk:** budget models may fail structured output or tool calls more often. Failed outputs lower scores for reasons unrelated to reasoning quality, and can hide real differences between configs
- **Mitigation:** hard gates before any bake-off call: structured outputs advertised, tool calling for the supervisor tier. Schema-valid rate is the first bake-off ranking criterion. No retry loop, so failures stay visible
- **Detection:** schema-valid rate per run and per agent, and a schema validation result on every trace span
- **If it happens:** when failures dominate bake-off or eval results, reconsider model tiers or staged slices ([ADR-028](decisions/ADR-028-cost-envelope.md#revisit-when)). What a single case records when an output fails validation at runtime is not decided

### Model retirement
- **Risk:** a pinned model or provider is retired, so new runs cannot match the published configuration
- **Mitigation:** published scores reproduce from the snapshot with no model access. The manifest names the model, provider, price, commit, and seed
- **Detection:** the provider stops serving the pinned slug, or its behavior changes. Standing trigger "cache staleness" in the [register](open-decisions.md#standing-triggers)
- **If it happens:** revisit per [ADR-007](decisions/ADR-007-one-cache-mechanism-two-lifecycle-points.md#revisit-when). The published snapshot stays valid for the results it recorded

## Cost

### Price snapshot staleness
- **Risk:** cost estimates rest on assumed prices and token counts. Gateway prices change, and reasoning models bill thinking tokens as output
- **Mitigation:** recheck candidate prices before the bake-off. Record the price at run time in the manifest. Replace estimates with measured token counts after the baseline run
- **Detection:** measured cost per case in the bake-off far from the estimate
- **If it happens:** revisit the ceiling and the run plan ([ADR-028](decisions/ADR-028-cost-envelope.md#revisit-when), DD-08)

### Spend overrun
- **Risk:** a runaway run or many cache misses exhaust the budget
- **Mitigation:** provisional $50 total ceiling. Per-case token and step caps. Dev runs replay from cache and cost nothing on a hit
- **Detection:** spend per run against the config limit. Cache miss count per run
- **If it happens:** the per-run spend abort stops the run, and the account-level limit on the gateway key stops all spend. When the ceiling is reached, reconsider staged slices ([ADR-028](decisions/ADR-028-cost-envelope.md#revisit-when)). The account-level limit setting is not verified yet

## Evaluation

### Judge self-preference
- **Risk:** an LLM judge that shares a model family with a graded agent may favor that agent's output
- **Mitigation:** no model grades a case. Grading is deterministic code against answer keys. The LLM judge for the drafted resident message is out of scope
- **Detection:** n/a while no judge exists
- **If it happens:** not decided. If a message judge is added, its model family choice is a new decision

### Small samples and leakage
- **Risk:** 5 planted homes per scenario cannot show statistical significance. Tuning on the published set would inflate scores
- **Mitigation:** every failure mode is a named count, never a percentage or composite. Prompt and code iteration uses a held-out 20-home dev set from a separate seed. Bake-off planted homes come from the dev set. Promotion thresholds are frozen with a dated git tag before multi-agent results are viewed (DD-03). Known overlap: the 25 bake-off clean homes are the published clean homes. Accepted to keep a full false-positive signal
- **Detection:** a first full eval too noisy to interpret. A threshold commit dated after multi-agent results exist
- **If it happens:** add homes beyond 60 (standing trigger "noisy eval", [ADR-006](decisions/ADR-006-evaluation-grading-rules.md#revisit-when)). If the baseline shows the non-negotiable criteria are unattainable on 60 homes, consider a larger case set ([ADR-019](decisions/ADR-019-promotion-criteria-and-threshold-freeze.md#revisit-when))

## Domain

### Rent pricing misuse
- **Risk:** algorithmic rent pricing draws legal and regulatory scrutiny. Output could be mistaken for a pricing tool
- **Mitigation:** the system has no send or write capability. It only recommends and records. A human approves every rent change and resident message. Code clamps every proposal to a global floor and cap. All market data is fictional
- **Detection:** clamp hits, graded as the pre-clamp row failing while the clamped row passes. Reviewer edits and approvals in the approval state
- **If it happens:** the clamp bounds the size of any change, and the audit snapshot records what was shown and who decided ([ADR-010](decisions/ADR-010-guardrails-tiering-and-audit-record.md)). The clamp (-5% to +6%) is calibrated to HUD Small Area Fair Market Rents ([DD-04](open-decisions.md))

### Protected characteristics reach a decision
- **Risk:** a protected characteristic in a structured field or a resident message shifts the rent or action
- **Mitigation:** protected structured fields are redacted in the data layer before any model, span, or trace sees them. The critic runs keyword rules plus a compliance classifier on the rationale and drafted message. Limit: free text cannot be redacted, so references in messages and work order notes reach the specialists by design
- **Detection:** compliance trap counts: detected, matched control, and influenced before the critic, reported separately so a strong critic cannot hide a weak specialist ([scenarios](scenarios.md#compliance-trap-pairs)). An influenced treated home is a severe miss, reported by home id
- **If it happens:** at runtime, a critic block ends the case in BLOCKED for manual review ([ADR-016](decisions/ADR-016-distinct-blocked-state.md)). In evaluation, if subtle or proxy variants still slip through, strengthen the classifier or add review ([ADR-004](decisions/ADR-004-critic-design.md#revisit-when))

### Outputs read as legal advice
- **Risk:** a reader treats the compliance checks or rent guidance as a legal review
- **Mitigation:** the project claims only what it checks, and says so here and in the README:
  - This project is not legal advice. Outputs are illustrative and must not drive real pricing or tenancy decisions without legal and compliance review
  - Compliance checks are a fixed rule list and one classifier. They cover the federal Fair Housing Act classes plus age, which is not a federal class and is included as a common bias pattern
  - State and local rules (rent caps, notice periods, source-of-income protections, local protected classes) are not modeled
  - Rent ranges and the clamp are calibrated to HUD and Census benchmarks, not to market renewal data (DD-04)
- **Detection:** n/a. Outside the system
- **If it happens:** the system cannot act on its own output. A human decides every renewal

### Synthetic data limits
- **Risk:** results are read as accuracy on real portfolios
- **Mitigation:** results are scoped to known planted cases, and the limits are stated:
  - All data is synthetic and fictional. No real residents, addresses, or messages
  - Causes are planted, histories are complete and clean, and there is no missing-data handling. Real records are messier
  - Each planted home carries one scenario's cause, so the eval does not measure stacked or ambiguous causes beyond the conflicting signals scenario
  - Pet damage is left out and would be added before production use ([ADR-012](decisions/ADR-012-data-scale-scenarios-and-variants.md))
  - Thresholds and severity tags are drafts until a generation run (DD-01)
- **Detection:** n/a. A limit of the method, not an event
- **If it happens:** production use would need a validation phase on real data. Not planned in this project

## Known gaps and open questions
- Runtime handling of a schema validation failure is not decided: whether the case records an error, a fail, or a distinct state. It affects grading and the recommendation schema
- Model family choice for a future message judge is not decided
- Gateway pinning options and the account-level spend limit are not verified (DD-02, DD-08)
- Likelihood and impact are not rated. No rating rubric exists. The PR template risk ratings (reach, reversibility, exposure, detection) also lack one
