# ADR-026: Keep approval and audit state in SQLite for release one, Lakebase as the target

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-009 (UI and state), ADR-010 (audit record), ADR-011 (local-first release), ADR-016 (BLOCKED state), ADR-027 (UI substitution) |
| **Pending** | DD-06 (Free Edition feasibility, including Lakebase), DD-09 (disposition vocabulary) |

## Context

Approval state is append-only: decision events, resolution events for BLOCKED and REJECTED ([ADR-016](ADR-016-distinct-blocked-state.md)), and an immutable audit snapshot per recommendation version ([ADR-010](ADR-010-guardrails-tiering-and-audit-record.md)). All of it goes through one repository interface ([ADR-009](ADR-009-streamlit-reviewer-ui-and-sqlite-state.md)).

## Decision

**Release one stores approval and audit state in SQLite. The target is Lakebase (managed Postgres). The repository interface is the seam.**

| | |
|---|---|
| Target | Lakebase Postgres database in the workspace |
| Release one | SQLite file on a shared Docker volume |
| Seam | Repository interface: append events, append snapshots, read history per case |

**Preserved by the stand-in**

- Append-only events and snapshots. No updates in place.
- Event and snapshot fields, and the history read by the UI.
- The rule that an approval-required recommendation cannot reach DONE without a decision event (ADR-010).

**Not preserved**

- Concurrent reviewers. SQLite is single-user here.
- Managed backups, availability, and on-behalf-of auth.

## Alternatives considered

- **Lakebase from the start.** Not chosen for release one. Needs a workspace, and its Free Edition support is unconfirmed.

## Consequences

**Benefits**

- No database server to run locally.
- The append-only rule is enforced in one place, the repository.

**Costs we accept**

- One reviewer at a time until the target is built.

## Revisit when

- Multiple or concurrent reviewers are needed (ADR-009).
- The Databricks phase starts and Lakebase is confirmed in the workspace ([DD-06](../open-decisions.md)).

## Known gaps and open questions

- Lakebase support on Free Edition is not confirmed. Doc versions disagree (DD-06).
- Resolution event disposition values are open ([DD-09](../open-decisions.md)).
