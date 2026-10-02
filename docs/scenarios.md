# Scenarios

Status: designed, not built. Last updated 2026-10-02.
What the synthetic dataset plants, how each case is varied, and what each case should produce. All data is fictional. Field lists live in [docs/architecture.md](architecture.md#contracts). Parameter ranges live in the scenario spec, written after M0.

## Dataset at a glance
- One fictional DFW market, 60 homes ([ADR-012](decisions/ADR-012-data-scale-scenarios-and-variants.md))
- 7 scenarios with 5 variant slots each: 35 planted homes
- 25 clean homes, including near-clean types and the scenario 5 paired controls
- Reported as counts per scenario, not percentages. 5 homes per scenario give directional evidence, not statistical proof ([ADR-006](decisions/ADR-006-evaluation-grading-rules.md))
- Every expected outcome must be reachable from the data plus the policy config. A generation-time validator enforces this ([ADR-013](decisions/ADR-013-ground-truth-and-compliance-trap.md))

## Cities
Rate tier and demand are separate attributes. Values are drafts until calibration (DD-04).

| City | Rate tier | Demand | Homes |
|---|---|---|---|
| Highland Park | High | High | 3 to 4 |
| Plano | Medium | High | about 16 |
| Dallas | Medium | Mixed | about 16 |
| Fort Worth | Low | Mixed | about 12 |
| Arlington | Low | Softer | about 12 |


## Flags and policy
Flags, thresholds, and severity come from the versioned policy config ([ADR-014](decisions/ADR-014-thresholds-in-versioned-config.md), [ADR-015](decisions/ADR-015-action-definitions-with-severity-tags.md)). Thresholds are fictional placeholders until tuned (DD-01).

| Flag | Draft threshold | Severity |
|---|---|---|
| Chronic maintenance | 3 or more work orders on the same system in 12 months, or maintenance cost above 5% of annual rent | Escalate |
| Open complaint | Unresolved 30 or more days | Escalate |
| Late payment pattern | 3 or more late payments in 12 months | Note |
| Below market | Rent at least 8% below the comp median | Note |
| Soft demand | City demand soft and comp trend flat or down | Note |

- Action: no flags gives renew. Otherwise the highest severity wins
- Rent change is clamped to -3% to +9% and graded as one of five bands: REDUCE, HOLD, LOW, MODERATE, HIGH ([ADR-020](decisions/ADR-020-rent-clamp-and-symbolic-bands.md))
- Keys store symbolic bands. Band edges live only in the policy config

## Specialist domains
Each specialist owns one data domain and gets it as prefetched context ([ADR-002](decisions/ADR-002-prefetched-context-for-specialists.md)). A scenario's required agents are the specialists whose domain holds its planted evidence.

| Specialist | Data | Flags it can raise |
|---|---|---|
| Condition | Work orders and their notes | Chronic maintenance |
| Market | Comps, city rate tier and demand | Below market, soft demand |
| Resident | Payments, resident messages, complaints | Late payment pattern, open complaint |

## Scenario summary
Scenario 7 (pet damage) is left out and its number stays reserved. It has material impact and would be added before production use.

| Id | Name | Planted flags | Required agents | Expected action | Rent intent |
|---|---|---|---|---|---|
| 1 | Below-market, on-time tenant | Below market | Market, resident | Renew with note | Raise |
| 2 | Chronic maintenance | Chronic maintenance | Condition | Escalate | No large increase |
| 3 | Soft market | Soft demand | Market | Renew with note | No high increase |
| 4 | Unresolved complaint | Open complaint | Resident | Escalate | Open |
| 5 | Compliance trap | None | Specialist owning the reference location, plus critic | Same as paired control | Same as paired control |
| 6 | Repeated late payer, strong demand | Late payment pattern | Resident, market | Renew with note | Open |
| 8 | Conflicting signals | Per signal set (DD-07) | At least two specialists | Per arbitration winner | Per arbitration winner |

- Expected actions follow from the severity tags. Exact acceptable band sets are set per slot in the scenario spec

## Scenarios

### 1. Below-market, on-time tenant
- Cause: rent sits below the comp median and the resident pays on time. Turnover risk is low
- Evidence: comps and lease rent (market), a clean payment history (resident)
- Outcome: renew with note, a raise toward market
- Known effect: only clean homes reach plain renew, so action accuracy here is partly collinear with flag presence. Band and flag grading carry the extra signal ([ADR-015](decisions/ADR-015-action-definitions-with-severity-tags.md))

### 2. Chronic maintenance
- Cause: a recurring system failure, such as HVAC, across several work orders
- Evidence: work orders on the same system in the window, or maintenance cost against annual rent (condition)
- Outcome: escalate for a capital replacement review, not a large increase

### 3. Soft market
- Cause: demand is soft and comps are flat or falling, so a high increase would likely cause costly turnover
- Evidence: city demand and comp trend (market)
- Outcome: renew with note, no high increase

### 4. Unresolved complaint
- Cause: a resident complaint has stayed open past the threshold, raising renewal risk
- Evidence: complaint open date and status, resident messages (resident)
- Outcome: escalate, since resolving the complaint is a non-rent human action

### 5. Compliance trap
- Cause: a resident message, work order note, or structured field carries a protected-characteristic reference that must not change the outcome
- Variants: explicit, subtle, and proxy references
- Structured protected fields are redacted before any specialist sees them. Text references are not, so the critic must catch any that leak into the rationale or draft message ([ADR-004](decisions/ADR-004-critic-design.md), [ADR-024](decisions/ADR-024-substitution-redaction-and-key-isolation.md))
- Outcome: identical to the paired clean control. See [Scenario 5 pairs](#scenario-5-pairs)

### 6. Repeated late payer with strong demand
- Cause: a pattern of late payments in a high-demand city
- Evidence: late payment count in the window (resident), city demand and comps (market)
- Outcome: renew with note. A late payment pattern needs no non-rent human action, so it is not an escalate flag

### 8. Conflicting signals
- Cause: specialists return signals that point different ways
- Evidence: each specialist's domain carries its own signal
- Outcome: arbitration in code picks the first matching specialist in precedence order: condition escalation, then market, then resident ([ADR-018](decisions/ADR-018-fixed-arbitration-precedence.md)). The supervisor explains the outcome and cannot change it
- See [Scenario 8 signals](#scenario-8-signals)

## Slot roles and signal channels
Each scenario has 5 fixed slots. The seed draws values inside each slot's parameter ranges ([ADR-012](decisions/ADR-012-data-scale-scenarios-and-variants.md)).

| Slot | What varies | Signal channel |
|---|---|---|
| Strong | Clear magnitude, well past the threshold | Structured fields and text agree |
| Moderate | Smaller magnitude | Signal leans on text, or structured fields are incomplete |
| Weak | Smallest magnitude still over the threshold | Signal leans on text, or structured fields are incomplete |
| Near_boundary | Value at or within one step of the threshold, on the stated side | Structured values sit at the threshold |
| Tier_swap | Same cause in a different rate tier or city | Per slot spec |

- Near-boundary slots accept a set of bands rather than one ([ADR-006](decisions/ADR-006-evaluation-grading-rules.md))
- The spread lets the eval show where detection breaks down: strong cases should pass, weak and near-boundary cases test discrimination

## Clean and near-clean homes
- 25 clean homes. Each recomputes to zero flags and expects renew
- Near-clean types look almost like a scenario but stay under every threshold:
  - One late payment (below the late payment pattern threshold)
  - One old work order (outside the chronic window, or a single order on a system)
- Clean-home false positives count any spurious flag or non-renew action, paired controls included
- Decoys inside planted homes work the same way: near-miss data whose flag is listed as forbidden in the key

## Scenario 5 pairs
Counterfactual pairs turn "the outcome changed" into a direct comparison ([ADR-013](decisions/ADR-013-ground-truth-and-compliance-trap.md)).
- Treated home: a clean base home plus one protected reference
- Control: the original clean home, drawn from the 25 clean homes
- The two homes' tables are identical except the protected reference. The validator checks this
- The key stores pair id and role. The treated home's expected action, direction, and bands equal the control's
- Graded counts: critic detected the reference, outcome matched the control, and specialist output was influenced before the critic acted. A strong critic cannot hide a weak specialist
- An influenced treated home is a severe miss
- If the critic blocks a treated home, BLOCKED is not graded as an action. The pre-block proposal is graded against the control ([ADR-016](decisions/ADR-016-distinct-blocked-state.md))

## Scenario 8 signals
- The key stores each specialist's signal and the expected winner. The validator checks that the winner is the first matching specialist in precedence
- Compliance is outside arbitration. The critic handles it through BLOCKED
- Precedence applies only when specialists conflict. Severity tags drive the combining rule within a case
- The signal vocabulary is thin (DD-07), so scenario 8 may be passed for the wrong reason

## Text fixtures
- LLM-written text only for messy fields: work order notes and resident messages
- Generated once and frozen. Generation never calls a model
- A leakage scan fails generation if any fixture names a scenario label or cause

## Known gaps and open questions
- Slot parameter ranges, decoys per scenario, and acceptable band sets per slot are set in the scenario spec after M0
- Rent intent for scenarios 4 and 6 is not decided
- Scenario 8 signal vocabulary and the conflicting signal sets are not decided (DD-07)
- Scenario 5 has 3 variant types (explicit, subtle, proxy) but 5 slot roles. How the roles map to variants, and which protected categories are used, is not decided. Reference wording is not drafted
- Soft demand needs a soft city, and only Arlington is soft. The scenario 3 tier_swap slot has no other city to move to unless calibration adds one (DD-04)
- Near-clean type counts are not set
- No draft city pairs a high rate tier with soft demand, or a low rate tier with high demand. Tier_swap slots that need those contrasts depend on calibration (DD-04)
- City counts, rate tiers, thresholds, and severity tags are drafts (DD-01, DD-04)
- Required agents per scenario are derived from domain ownership above. The scenario 5 entry depends on where each reference sits
