# ADR-013: Build ground truth by construction and test the compliance trap with paired controls

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-006 (grading), ADR-010 (guardrails), ADR-012 (data scale), ADR-014 (thresholds), ADR-024 (redaction and key isolation) |
| **Pending** | None |

## Context

If a human could not reach the answer key from the data plus the policy, the grade is invalid.

The compliance trap scenario tests whether a reference to a protected characteristic changes the outcome. That needs a control: the same home without the reference.

## Decision

**Keys are hand-authored per slot and checked by a generation-time validator. The compliance trap uses counterfactual pairs.**

**Answer keys**

- Each slot has hand-authored intent. Each key entry lists the evidence that makes the outcome derivable: table, record id, field, value, rule, and text spans.
- The validator checks the generated evidence against the stated rule. Generation fails on any mismatch.
- Validator rules are versioned with the key.

**Isolation and leakage**

- Keys live in a restricted directory outside the agent-readable data path ([ADR-024](ADR-024-substitution-redaction-and-key-isolation.md)).
- Opaque home ids and shuffled row order.
- A leakage scan on frozen text fixtures: no scenario labels or cause names.

**Compliance trap scenario**

- Preventive control: protected-characteristic structured fields are redacted before any specialist sees them ([ADR-010](ADR-010-guardrails-tiering-and-audit-record.md)).
- Explicit, subtle, and proxy variants. Measure the catch rate and whether redaction held.
- **Counterfactual pairs:** the treated home is a clean base home plus the protected reference. Its matched control is the original clean home, drawn from the 25 clean homes.
  - The key stores pair id and role.
  - The treated home's expected outcome equals the control's.
  - Controls must be plain clean homes. Clean-home false-positive counts include them.

## Alternatives considered

- **Derive keys automatically from generated data.** Rejected. A key computed by the generator only proves the generator agrees with itself, not that the intent was planted.
- **Label scenarios by hand after generation.** Rejected. Not reproducible from a seed, and labels can drift from the evidence.

## Consequences

**Benefits**

- Every key is reachable from cited evidence, so a failed case points at the agent, not the data.
- Paired controls turn "the outcome changed" into a direct comparison.

**Costs we accept**

- Hand-authored intent per slot takes effort.
- Using clean homes as controls slightly reduces the independent clean-home count.

## Revisit when

- The validator cannot express a scenario's rule without code that duplicates the generator.

## Known gaps and open questions

- Final key and spec field lists are set when the schemas are committed (after M0).
- Protected-reference wording per variant is not drafted yet.
