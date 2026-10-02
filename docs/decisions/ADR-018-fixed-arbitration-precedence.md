# ADR-018: Resolve specialist conflicts with a fixed precedence list

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-003 (logic stays code), ADR-012 (scenarios), ADR-013 (ground truth), ADR-015 (severity tags), ADR-016 (BLOCKED state) |
| **Pending** | DD-07 (scenario 8 signal vocabulary) |

## Context

Scenario 8 plants conflicting signals between specialists to test how disagreement is handled. The model can explain a resolution, but the resolution itself must be reproducible and gradable.

## Decision

**A fixed precedence list in the policy config decides conflicts. Code decides, the model explains.**

- **Order:** condition escalation, then market, then resident.
- **Compliance is outside arbitration.** The critic handles it through the BLOCKED state (ADR-016).
- **Scope:** precedence applies only when specialists conflict. Severity tags (ADR-015) drive the combining rule within a case. Overlap between the two is watched.
- **Keys:** for scenario 8, the key stores the signals and the expected winner. The validator checks that the winner is the first matching specialist in precedence order.
- The supervisor's arbitration note explains the code's outcome. It cannot change it.

## Alternatives considered

- **Supervisor decides freely.** Rejected. Outcomes vary by run and cannot be derived from data plus policy.
- **Confidence-weighted voting.** Rejected. Model confidence is not calibrated, and the key would depend on model output.

## Consequences

**Benefits**

- Arbitration outcomes are predictable, reproducible, and gradable.
- Changing the order is a config change.

**Costs we accept**

- A fixed order cannot weigh evidence strength.
- The conflict signal vocabulary is thin, so scenario 8 may be passed for the wrong reason.

## Revisit when

- Arbitration outcomes disagree with severity-tag outcomes in generated cases.
- The signal vocabulary is expanded (DD-07).

## Known gaps and open questions

- Scenario 8 signal vocabulary is thin (DD-07).
