# ADR-012: Generate 60 homes across 7 scenarios with seeded variant slots

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-006 (grading), ADR-013 (ground truth), ADR-014 (thresholds), ADR-018 (arbitration), ADR-021 (storage) |
| **Pending** | None. DD-04 decided 2026-10-03 |

## Context

Grading needs planted, known causes plus clean background homes, so every key can be derived from the data. The dataset must stay small enough to generate, review, and evaluate by hand, which limits statistical power.

## Decision

**One fictional market (DFW), 60 homes: 7 scenarios with 5 seeded variant slots each (35 planted homes) plus 25 clean homes.**

**Market and cities**

- Fictional data, calibrated to HUD Small Area Fair Market Rents (SAFMRs, ZIP-level rent benchmarks) FY2027 and Census ACS 2020 to 2024 ([DD-04](../open-decisions.md), 2026-10-03). Figures and scripts: [research/dd-04-calibration](../../research/dd-04-calibration/README.md).
- Cities carry separate rate tier and demand attributes:

| City | Rate tier | Demand | Homes |
|---|---|---|---|
| Highland Park | High | High | 3 to 4 |
| Prosper | High | Soft | 3 |
| Plano | Medium | High | about 13 |
| Dallas | Medium | Mixed | about 13 |
| Lewisville | Low | High | 4 |
| Fort Worth | Low | Mixed | about 12 |
| Arlington | Low | Soft | about 12 |

- Prosper adds high rent with soft demand, and Lewisville adds low rent with strong demand. Every rate tier then has a contrasting demand value, so tier_swap slots can move a cause across tiers. Prosper also gives the soft market scenario a soft city outside the low tier.
- Base monthly rent per rate tier, for a generated single-family home, anchored on the SAFMR FY2027 3-bedroom city medians:

| Rate tier | Base rent range | Sourced 3-bedroom city medians |
|---|---|---|
| Low | $1,800 to $2,400 | Dallas $2,090, Fort Worth $2,210, Arlington $2,405 |
| Medium | $2,400 to $3,000 | Lewisville $2,365, Plano $2,815 |
| High | $3,000 to $3,600 | Prosper $3,260, Highland Park $3,410 |

- Rate tiers are fictional labels anchored to these ranges. Two placements depart from the sourced ranking: Dallas ranks low, not medium, and Lewisville ranks medium, not low. They are kept so every rate tier has a contrasting demand value for tier_swap slots. Following the sourced ranking would leave the low tier with no high-demand city and the medium tier with only high demand.

**Scenarios**

- 1 below-market on-time tenant, 2 chronic maintenance, 3 soft market, 4 unresolved complaint, 5 compliance trap, 6 repeated late payer with strong demand, 8 conflicting signals.
- Pet damage (scenario 7) is left out. It has material impact and would be added before production use. Its number stays reserved.

**Variant slots**

- Each scenario has 5 fixed slots: strong, moderate, weak, near_boundary, tier_swap.
- Each slot has parameter ranges and a city constraint. The seed picks values inside the ranges.
- Signal channel is set by slot role:
  - Strong: structured fields and text agree.
  - Moderate and weak: the signal leans on text, or structured fields are incomplete.
  - Near-boundary: structured values sit at the policy threshold ([ADR-014](ADR-014-thresholds-in-versioned-config.md)).
- Clean homes include near-clean types (one late payment, one old work order) to test discrimination.

**Tables and text**

- Core tables: homes, leases, payments, work orders, comps. `market_id` on every table.
- LLM-written text only for messy fields (notes, messages), generated once and frozen as fixtures.
- Storage is Parquet ([ADR-021](ADR-021-substitution-storage.md)). Reporting uses counts per scenario ([ADR-006](ADR-006-evaluation-grading-rules.md)).

## Alternatives considered

- **Several markets, 300 or more homes.** Rejected for release one. Generation, review, and eval cost grow with no new failure modes covered.
- **Fewer scenarios with more variants each.** Rejected. Fewer causes means fewer agent behaviors tested, and arbitration (conflicting signals scenario) and the compliance trap both need their own scenarios.

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

- Home counts per city are drafts until the scenario spec assigns slots.
- Slot parameter ranges are set in the scenario spec (planned).
