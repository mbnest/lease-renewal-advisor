# ADR-020: Clamp rent changes globally and grade against symbolic bands

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-003 (economics in code), ADR-006 (grading), ADR-009 (reviewer edits), ADR-012 (market calibration), ADR-014 (policy config) |
| **Pending** | DD-04 (calibrate the clamp and city rate tiers to sourced DFW ranges) |

## Context

Algorithmic rent pricing draws legal and regulatory scrutiny. The system is advisory and uses fictional data.

Scenario logic should come from evidence and agent reasoning, not from the clamp.

Secondary sources checked on 2026-10-02 show 2026 metro rents falling year over year, so a +9% cap is generous against the trend. README citations will use primary sources: HUD FY2026 Small Area Fair Market Rents and Census ACS.

## Decision

**A global floor and cap clamp every rent proposal in code. Answer keys store one of five named bands, resolved by the policy config.**

- **Model proposes, code enforces.** The economics function supplies guidance, not enforcement (ADR-003).
- **Clamp:** floor -3%, cap +9%. Fictional placeholders until calibration (DD-04), including whether to lower the cap.
- **Bands (percent change):**

| Band | Range | Direction |
|---|---|---|
| REDUCE | -3 up to but excluding 0 | Reduce |
| HOLD | Exactly 0 | Hold |
| LOW | Above 0 to 3 | Raise |
| MODERATE | Above 3 to 6 | Raise |
| HIGH | Above 6 to 9 | Raise |

- Keys store symbolic bands. Band edges live only in the policy config.
- Grading uses direction and band, on both the pre-clamp proposal and the clamped output (ADR-006).
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
- Calibration shows the placeholder clamp is unrealistic for the sourced ranges (DD-04).

## Known gaps and open questions

- Clamp and band edges are placeholders until calibration (DD-04).
