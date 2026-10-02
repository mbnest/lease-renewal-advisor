# ADR-012: Generate 60 homes across 7 scenarios with seeded variant slots

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-006 (grading), ADR-013 (ground truth), ADR-014 (thresholds), ADR-018 (arbitration), ADR-021 (storage) |
| **Pending** | DD-04 (rent and city rate calibration), DD-07 (scenario 8 signal vocabulary) |

## Context

Grading needs planted, known causes plus clean background homes, so every key can be derived from the data. The dataset must stay small enough to generate, review, and evaluate by hand, which limits statistical power.

## Decision

**One fictional market (DFW), 60 homes: 7 scenarios with 5 seeded variant slots each (35 planted homes) plus 25 clean homes.**

**Market and cities**

- Fictional data, calibrated to rough real-world rent ranges. Sources go in the README (DD-04).
- Cities carry separate rate tier and demand attributes. Draft values:

| City | Rate tier | Demand | Homes |
|---|---|---|---|
| Highland Park | High | High | 3 to 4 |
| Plano | Medium | High | about 16 |
| Dallas | Medium | Mixed | about 16 |
| Fort Worth | Low | Mixed | about 12 |
| Arlington | Low | Softer | about 12 |

**Scenarios**

- 1 below-market on-time tenant, 2 chronic maintenance, 3 soft market, 4 unresolved complaint, 5 compliance trap, 6 repeated late payer with strong demand, 8 conflicting signals.
- Scenario 7 (pet damage) is left out. It has material impact and would be added before production use. Its number stays reserved.

**Variant slots**

- Each scenario has 5 fixed slots: strong, moderate, weak, near_boundary, tier_swap.
- Each slot has parameter ranges and a city constraint. The seed picks values inside the ranges.
- Signal channel is set by slot role:
  - Strong: structured fields and text agree.
  - Moderate and weak: the signal leans on text, or structured fields are incomplete.
  - Near-boundary: structured values sit at the policy threshold (ADR-014).
- Clean homes include near-clean types (one late payment, one old work order) to test discrimination.

**Tables and text**

- Core tables: homes, leases, payments, work orders, comps. `market_id` on every table.
- LLM-written text only for messy fields (notes, messages), generated once and frozen as fixtures.
- Storage is Parquet (ADR-021). Reporting uses counts per scenario (ADR-006).

## Alternatives considered

- **Several markets, 300 or more homes.** Rejected for release one. Generation, review, and eval cost grow with no new failure modes covered.
- **Fewer scenarios with more variants each.** Rejected. Fewer causes means fewer agent behaviors tested, and arbitration (scenario 8) and the compliance trap (scenario 5) both need their own scenarios.

## Consequences

**Benefits**

- Every planted cause has a strong, a weak, and a near-boundary case, so the eval shows where detection breaks down.
- Seeded slots make the dataset reproducible and tunable.

**Costs we accept**

- 5 planted homes per scenario give directional evidence, not statistical proof. The README says so.
- Calibration to real ranges is approximate, and 2026 metro rents are falling.

## Revisit when

- The first full eval is too noisy to interpret. Add homes beyond 60.

## Known gaps and open questions

- City counts and rate values are drafts until calibration (DD-04).
- Scenario 8 signal vocabulary is thin (DD-07).
- Slot parameter ranges are set in the scenario spec (planned).
