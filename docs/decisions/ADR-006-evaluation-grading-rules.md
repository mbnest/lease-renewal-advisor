# ADR-006: Grade with separate named counts, not a composite score

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-012 (data scale), ADR-013 (ground truth), ADR-016 (BLOCKED state), ADR-020 (rent clamp and bands), ADR-028 (run plan) |
| **Pending** | None |

## Context

Ground truth is planted in synthetic data, so grading against answer keys is deterministic.

Two parts of the design can hide errors:

- **The rent clamp** can turn a bad model proposal into an acceptable output.
- **The critic** can block a case and hide a weak specialist behind it.

The evaluation set is 60 homes across 7 scenarios. That gives directional evidence, not statistical proof.

## Decision

**Every failure mode is reported as its own count, per scenario. No percentages, no composite score.**

**Rent**

- Headline: pass or fail on direction (raise, hold, reduce) and on the policy clamp.
- Band: two raw counts, exact and within one band. Near-boundary variants accept a set of bands.
- The pre-clamp proposal is graded as well as the clamped output.

**Action (renew, renew with note, escalate)**

- Headline: strict three-way match, with a confusion matrix always generated.
- BLOCKED is not graded as an action. The pre-block proposal is graded separately.
- **Severe misses** are a named count, not a weight: an escalate case labeled renew, or a compliance-trap case influenced by the protected reference.

**Flags and compliance (home level, with a flag-level detail table)**

- Flag recall: planted homes with all required flags.
- Clean-home false positives: clean homes with any spurious flag or a non-renew action, paired controls included.
- Compliance: the critic detected the protected reference; the outcome matched the control; and specialist output was influenced before the critic acted.
- Blocked count, false blocks on clean homes, and threshold misapplied count.
- Detail table: recall per flag, spurious flags per clean home and per decoy.

**Conflicting signals scenario**

- Arbitration winner and direction against the key, per slot, and each specialist's signal against the key (ADR-018). These expose a right outcome reached for the wrong reason.

**Comparison and consistency**

- Baseline and multi-agent are compared case by case.
- Repeated runs are scored by majority, with flip rate reported separately. Which configurations get repeated runs is set in ADR-028.

## Alternatives considered

- **Weighted scores, with severe misses as weights.** Rejected. A weight lets many small wins cancel a severe miss.
- **Percentages and a single composite score.** Rejected. With 5 planted homes per scenario, percentages overstate precision, and a composite hides which failure mode moved.

## Consequences

**Benefits**

- No failure mode hides behind another: the clamp, the critic, and the action each have their own count.
- The influenced-before-critic count keeps a strong critic from masking a weak specialist.

**Costs we accept**

- Many counts are harder to summarize than one score.
- Small per-scenario counts are directional only. The README says so.

## Revisit when

- The first full eval is too noisy to interpret. Add homes beyond 60 (ADR-012).

## Known gaps and open questions

- None. Exact scoring rules per count live in [docs/eval-plan.md](../eval-plan.md).
