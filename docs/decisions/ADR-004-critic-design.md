# ADR-004: Verify claims in code and check compliance with rules plus one classifier

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-003 (logic stays code), ADR-014 (thresholds in config), ADR-016 (BLOCKED state) |
| **Pending** | None |

## Context

Before anything reaches a reviewer, the critic must catch two kinds of failure.

**Unsupported claims**, for example:

- a number not in the data, or a wrong count
- causation the evidence does not support
- a draft message promising something the recommendation does not
- a finding attributed to the wrong specialist

**Prohibited reasoning**, often paraphrased rather than explicit, for example:

- "large household, likely heavy wear"
- "single mother, may struggle with the increase"
- "elderly tenant, unlikely to move"
- references to a church group
- disability modification requests counted as "high-maintenance"
- "neighborhood is changing" used as a proxy

## Decision

**Claims are verified in code. Compliance is checked by keyword rules plus one narrow LLM classifier.**

- **Claims.** Every claim carries evidence references (record ids and cited values), which code verifies. A typed claim vocabulary limits what agents can assert.
- **Compliance.** Keyword rules, plus one classifier run on the final rationale and the drafted message. Its output is a schema-validated verdict with a quoted span. It has no tools.
- The critic does not recompute policy thresholds at runtime (ADR-014).
- A block puts the recommendation in the BLOCKED state (ADR-016).
- Ablation: rules only, against rules plus classifier, on explicit and subtle variants.

## Alternatives considered

- **A fully LLM critic.** Rejected. Claim checks are exact in code, and a model would add cost and nondeterminism to them.
- **Keyword rules only.** Rejected as the design, kept as the ablation arm. Rules cannot judge paraphrase or proxies.

## Consequences

**Benefits**

- Claim checks are cheap, deterministic, and unit-testable.
- The classifier covers paraphrase, and the ablation measures what it adds.

**Costs we accept**

- One extra model call per case, with some nondeterminism.
- A typed claim vocabulary restricts what agents can say.

## Revisit when

- The ablation shows rules only catch the same variants as rules plus classifier. Drop the classifier.
- Evaluation shows subtle or proxy variants still slipping through. Strengthen the classifier or add review.

## Known gaps and open questions

- The claim vocabulary is not defined yet. It lands with the contract schemas.
