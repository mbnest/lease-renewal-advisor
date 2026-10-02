# ADR-010: Enforce guardrails in code, with an approval gate and an audit record

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-009 (approval state), ADR-016 (BLOCKED state), ADR-019 (promotion criteria) |
| **Pending** | DD-03 (numeric promotion thresholds) |

## Context

Algorithmic rent pricing draws legal and regulatory scrutiny. The system is advisory: a human decides every renewal.

Guardrails stated only in documentation can be bypassed by a code change. They need to be structural, and tested.

## Decision

**The system has no send or write capability. It only recommends and records.**

- **Tiers:** RECORD_ONLY and APPROVAL_REQUIRED. Every recommendation is APPROVAL_REQUIRED in release one.
- **Gate states:** DRAFTED, BLOCKED, PENDING_APPROVAL, APPROVED, REJECTED, DONE. A recommendation that requires approval cannot reach DONE without a decision event. BLOCKED routes to the manual-review queue.
- **Audit record:** an immutable snapshot of the recommendation version at DRAFTED, stored next to decision events through the same repository interface (ADR-009). JSON export for published samples.
- Reproducibility metadata (model id, prompt versions, policy config, git commit, data seed) lives in trace attributes, MLflow run params, and the snapshot manifest, not in the audit record.
- Promotion from APPROVAL_REQUIRED to RECORD_ONLY is documented, not built (ADR-019).
- Tests: the codebase has no send or write path, and no approval-required recommendation reaches DONE without a decision event.

## Alternatives considered

- **Guardrails in documentation only.** Rejected. Nothing stops a later change from breaking them.
- **Full autonomy tiers built now.** Rejected. No evaluation results exist to justify promoting any recommendation type.
- **Hash-chained audit records.** Deferred. It can be added later without changing the record.

## Consequences

**Benefits**

- The approval rule is enforced by code and tests, not by convention.
- Every recommendation shown to a reviewer has an immutable snapshot.

**Costs we accept**

- Every recommendation needs a human decision, so automation gives no throughput gain yet.
- The audit snapshot duplicates some recommendation content.

## Revisit when

- A past recommendation must be explained after a prompt or policy change, and the minimal record plus traces cannot do it.

## Known gaps and open questions

- Numeric promotion thresholds are set after the baseline run (DD-03).
