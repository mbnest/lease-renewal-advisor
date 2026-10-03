# ADR-020: Clamp rent changes globally and grade against symbolic bands

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-003 (economics in code), ADR-006 (grading), ADR-009 (reviewer edits), ADR-012 (market calibration), ADR-014 (policy config) |
| **Pending** | None. DD-04 decided 2026-10-03 |

## Context

Algorithmic rent pricing draws legal and regulatory scrutiny. The system is advisory and uses fictional data.

Scenario logic should come from evidence and agent reasoning, not from the clamp.

Calibration ([DD-04](../open-decisions.md), 2026-10-03) used primary sources: HUD Small Area Fair Market Rents (SAFMRs, ZIP-level rent benchmarks) and Census ACS. Across 98 ZIPs in the seven cities, the 3-bedroom SAFMR changed from FY2026 to FY2027 by a median of -5.5%, with a range of -9.9% to +4.2%. The earlier +9% cap was generous against that trend. Figures and scripts: [research/dd-04-calibration](../../research/dd-04-calibration/README.md).

## Decision

**A global floor and cap clamp every rent proposal in code. Answer keys store one of five named bands, resolved by the policy config.**

- **Model proposes, code enforces.** The economics function supplies guidance, not enforcement ([ADR-003](ADR-003-economics-and-critic-logic-stay-code.md)).
- **Clamp:** floor -5%, cap +6% (DD-04). The floor reaches the sourced median drop, so soft market reductions are realistic. The cap keeps headroom above the largest sourced rise.
- **Bands (percent change):**

| Band | Range | Direction |
|---|---|---|
| REDUCE | -5 up to but excluding 0 | Reduce |
| HOLD | Exactly 0 | Hold |
| LOW | Above 0 to 2 | Raise |
| MODERATE | Above 2 to 4 | Raise |
| HIGH | Above 4 to 6 | Raise |

- Keys store symbolic bands. Band edges live only in the policy config.
- Grading uses direction and band, on both the pre-clamp proposal and the clamped output ([ADR-006](ADR-006-evaluation-grading-rules.md)).
- The README cites sources. [docs/risks.md](../risks.md#not-legal-advice) notes "not legal advice."

## Alternatives considered

- **Per-scenario or per-city caps.** Rejected. The clamp would encode scenario logic and hide whether the agents found it.
- **Free numeric increases with no clamp.** Rejected. Nothing in code would stop an extreme proposal.

## Consequences

**Benefits**

- The clamp is a simple, testable outer guardrail.
- Symbolic bands survive recalibration. Only the config changes.

**Costs we accept**

- A global clamp is a weak policy model.
- The clamp can mask model errors, so the pre-clamp proposal must be graded too.

## Revisit when

- Band counts are uninformative in the first full eval.
- A new HUD SAFMR release moves the pooled year-over-year median below the floor, or its largest rise above the cap.

## Known gaps and open questions

- SAFMR is a 40th percentile benchmark for voucher payment standards, not a renewal increase. The clamp rests on it as the best public primary source.
