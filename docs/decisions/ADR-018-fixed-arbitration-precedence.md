# ADR-018: Resolve specialist conflicts with a fixed precedence list

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-003 (logic stays code), ADR-012 (scenarios), ADR-013 (ground truth), ADR-015 (severity tags), ADR-016 (BLOCKED state) |
| **Pending** | None |

## Context

Scenario 8 plants conflicting signals between specialists to test how disagreement is handled. The model can explain a resolution, but the resolution itself must be reproducible and gradable.

## Decision

**A fixed precedence list in the policy config decides conflicts. Code decides, the model explains.**

- **Order:** condition escalation, then market, then resident.
- **Compliance is outside arbitration.** The critic handles it through the BLOCKED state (ADR-016).
- **Scope:** arbitration decides rent direction only, and only when specialist signals imply different directions. Severity tags (ADR-015) still decide the action, so the two never overlap.
- **Signals:** each specialist output carries one directional signal. Condition: ESCALATE, RAISE, NONE. Market: RAISE, HOLD, NONE. Resident: RAISE, HOLD, NONE. Only ESCALATE matches for condition. Values live in the policy config. Slot design is in `docs/scenarios.md`.
- **Keys:** for scenario 8, the key stores the signals, the expected winner, and the direction. The validator checks that the winner is the first matching specialist in precedence order and that the direction is the winner's.
- The supervisor's arbitration note explains the code's outcome. It cannot change it.
- **Order:** arbitration runs in code on the specialist outputs, before the supervisor. The supervisor receives the outcome and writes the note (ADR-001).

## Alternatives considered

- **Supervisor decides freely.** Rejected. Outcomes vary by run and cannot be derived from data plus policy.
- **Confidence-weighted voting.** Rejected. Model confidence is not calibrated, and the key would depend on model output.

## Consequences

**Benefits**

- Arbitration outcomes are predictable, reproducible, and gradable.
- Changing the order is a config change.

**Costs we accept**

- A fixed order cannot weigh evidence strength.
- The signal vocabulary is small, so scenario 8 may still be passed for the wrong reason.
- Arbitration cannot change the action, even when the winning specialist's domain would argue for one.

## Revisit when

- Generated cases show a winner's direction that contradicts the action, such as a raise on an escalate case.
- Scenario 8 results suggest the vocabulary is too small to separate right and wrong reasoning.

## Known gaps and open questions

- The signal field in the specialist output schema is set with the schemas after M0.
