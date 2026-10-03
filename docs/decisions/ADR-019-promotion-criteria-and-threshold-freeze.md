# ADR-019: Fix promotion non-negotiables now, freeze numeric thresholds after baseline

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-006 (grading), ADR-010 (tiers and gate states), ADR-012 (data scale) |
| **Pending** | DD-03 (numeric thresholds, frozen after baseline and before multi-agent results are viewed) |

## Context

Every recommendation is APPROVAL_REQUIRED in release one ([ADR-010](ADR-010-guardrails-tiering-and-audit-record.md)). Moving a recommendation type to RECORD_ONLY needs criteria that are set before the evidence that would justify it.

Setting thresholds after seeing multi-agent results would invite tuning them to the result.

## Decision

**Non-negotiable criteria are fixed now. Numeric thresholds are committed with a dated freeze after the baseline run and before multi-agent results are viewed.**

- **Fixed now:** zero compliance misses, zero severe misses, flip rate reported against a cap, and a minimum case count before any promotion.
- **Frozen later:** numeric values, such as action match counts and the flip rate cap. Committed in this ADR with a dated freeze and a git tag `freeze-dd03-YYYYMMDD`.
- **Scope:** promotion applies per recommendation type, from APPROVAL_REQUIRED to RECORD_ONLY.
- **Not built** in release one. The path is documented only.

## Alternatives considered

- **Set all numbers now.** Rejected. With no baseline, the numbers would be guesses.
- **Set numbers after all results.** Rejected. The thresholds could be fitted to the multi-agent results they are meant to judge.

## Consequences

**Benefits**

- The criteria cannot be fitted to the results they judge.
- The git tag makes the freeze date checkable.

**Costs we accept**

- Part of the criteria stays open until the baseline exists.
- The freeze depends on viewing results in the right order.

## Revisit when

- The baseline shows the non-negotiables are unattainable on 60 homes. Consider a larger case set ([ADR-012](ADR-012-data-scale-scenarios-and-variants.md)).

## Known gaps and open questions

- Numeric thresholds are not set ([DD-03](../open-decisions.md)).
- No mechanism enforces the viewing order. It relies on process alone.
