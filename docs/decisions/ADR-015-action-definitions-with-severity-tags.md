# ADR-015: Define actions semantically, with severity tags in config

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-006 (grading), ADR-014 (thresholds), ADR-016 (BLOCKED state), ADR-018 (arbitration) |
| **Pending** | DD-01 (tag review after the first generation run) |

## Context

The action label must be derivable from data plus policy, or grading is invalid. It should also carry information beyond whether any flag was raised.

## Decision

**Three actions with semantic definitions. Each flag type carries a severity tag in the policy config. Highest severity wins.**

| Action | Definition |
|---|---|
| Escalate | A non-rent human action is needed |
| Renew with note | Proceed, with a flagged item for the reviewer |
| Renew | No flags |

| Severity | Flag types |
|---|---|
| Escalate | Chronic maintenance, open complaint |
| Note | Late payment pattern, below market, soft demand |

## Alternatives considered

- **Mechanical severity table (flag counts and combinations).** Rejected. The action becomes collinear with flag recall and adds no signal.
- **Actions from model confidence or signal conflict.** Rejected. Not derivable from data plus policy.
- **An info severity that maps to renew.** Rejected. It reopens "renew means no flags."
- **Late payment as escalate.** Rejected. It needs no non-rent human action, so it fails the escalate definition.

## Consequences

**Benefits**

- Each action has a plain meaning a reviewer can check.
- Tags live in config, so they can be tuned without code changes.

**Costs we accept**

- Scenario 1 (below market, on time) lands on renew with note. Only clean homes get plain renew, so action accuracy is partly collinear with flag presence. Rent band and flag grading carry the extra signal.
- Severity is fixed per flag type. Context cannot soften or harden it.

## Revisit when

- The first generation run shows the action label tracks flag presence and adds no information. Reconsider tags or add an info severity.

## Known gaps and open questions

- Tag assignments are reviewed after the first generation run (DD-01).
