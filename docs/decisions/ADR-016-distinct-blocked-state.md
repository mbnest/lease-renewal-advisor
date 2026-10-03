# ADR-016: Send critic blocks to a distinct BLOCKED state

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-004 (critic), ADR-006 (grading), ADR-009 (approval state), ADR-010 (gate states), ADR-026 (state substitution) |
| **Pending** | DD-09 (resolution event disposition vocabulary) |

## Context

When the critic blocks a case, the result must not be mistaken for an action recommendation. Forcing a blocked case into an action would muddy action accuracy.

## Decision

**A critic block moves the case to a terminal BLOCKED state and a manual-review queue. It is counted separately and never graded as an action.**

- **Grading:** report the blocked count and false blocks on clean homes. The pre-block proposal is graded separately (ADR-006).
- **Pre-block proposal:** retained on the recommendation for grading. Never shown as a draft.
- **BLOCKED card:** shows the critic reason and no draft message.
- **Terminal states:** BLOCKED and REJECTED are both terminal gate states.
- **Resolution event:** each records one in the same append-only table: case id, recommendation version, disposition, reviewer, timestamp, reason. It is not a new gate state.
- **Reruns:** a rerun after BLOCKED or REJECTED is a new recommendation version, never a transition back to DRAFTED.

## Alternatives considered

- **Force ESCALATE and withhold the draft.** Rejected. Blocked cases would count as escalations and distort action accuracy.
- **One regeneration pass, then fail closed.** Rejected. It adds a retry loop, and the regenerated output would be graded as if it were the first proposal.
- **REJECTED returns to DRAFTED.** Rejected. It reintroduces the retry loop and breaks the one-version, one-outcome history.

## Consequences

**Benefits**

- Action accuracy counts only real action proposals.
- Every version has one terminal outcome, so the audit history stays linear.

**Costs we accept**

- A reviewer cannot resolve a blocked case in the app beyond recording a disposition.
- A strong critic can hide a weak specialist. The compliance trap scenario reports treated homes influenced before the critic acted as a separate count (ADR-006).

## Revisit when

- False blocks on clean homes are high.
- The manual-review queue becomes the main reviewer workload.

## Known gaps and open questions

- Disposition values are not defined yet (DD-09). They are set when the recommendation schema is written.
