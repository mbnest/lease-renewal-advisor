# ADR-014: Keep policy thresholds in versioned config, with no runtime recompute

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-004 (critic), ADR-006 (grading), ADR-013 (ground truth), ADR-015 (action definitions) |
| **Pending** | DD-01 (tuned threshold values) |

## Context

Agents and graders must work from the same stated policy, or the key is not derivable from data plus policy.

Draft thresholds. Fictional placeholders, tuned after the first generation run:

| Flag | Draft threshold |
|---|---|
| Chronic maintenance | 3 or more work orders on the same system in 12 months, or maintenance cost above 5% of annual rent |
| Late payment pattern | 3 or more late payments in 12 months. 1 or 2 is a decoy |
| Below market | Rent at least 8% below the comp median |
| Soft demand | City demand soft and comp trend flat or down |
| Open complaint | Unresolved 30 or more days |

## Decision

**Thresholds live in one versioned policy config that agents see. Nothing recomputes them at runtime.**

- The generation-time validator is the only code that evaluates thresholds. It reads the same config.
- The critic still verifies every cited value and record id (ADR-004). It does not re-derive flags.
- Misapplied thresholds are found at grading time, as a "threshold misapplied" count (ADR-006).
- The policy version is recorded on every recommendation.

## Alternatives considered

- **Critic recomputes structured flags in code and checks quoted spans for text flags.** Rejected for now. It duplicates the validator's rules in a second place, and grading already catches misapplication.
- **Thresholds only in the key and validator.** Rejected. Agents could not see the policy, so the key would not be derivable from data plus policy.

## Consequences

**Benefits**

- One rule implementation, in the validator. A simpler critic.
- Changing a threshold is a config change with a version bump.

**Costs we accept**

- A misapplied threshold can reach the reviewer. It is only counted after the fact.

## Revisit when

- Threshold misapplication clusters in eval results. Then reconsider the critic recompute.

## Known gaps and open questions

- Threshold values are placeholders until the first generation run (DD-01).
- Config file name and format are set with the schemas (after M0).
