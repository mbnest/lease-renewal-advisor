# ADR-009: Review in Streamlit with append-only SQLite state

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Related** | ADR-010 (guardrails), ADR-016 (BLOCKED state), ADR-020 (rent clamp), ADR-026 (state substitution), ADR-027 (UI substitution) |
| **Pending** | DD-06 (Free Edition feasibility for apps and Lakebase) |

## Context

The reviewer is a non-technical operations or revenue person. The system only recommends and records, so every approval or rejection must be auditable.

The data covers one market (DFW), so the market level is a header total rather than its own chart.

## Decision

**Streamlit is the only UI, with approval state in SQLite behind a repository interface.**

- **Pages:** approval page, per-home card, and an operational dashboard with rollups by city.
- **`market_id`** is present in all tables, so more markets need no schema change.
- **Approval state:** append-only decision events (case id, recommendation version, action, reviewer, timestamp, reason). BLOCKED and REJECTED cases also record a resolution event in the same table (ADR-016).
- **Reviewer powers:** approve or reject only. The contract leaves room for edits, but any edit path must rerun the rent clamp (ADR-020) and the critic before it can be approved.
- **Per-home card:** a summary header (action, rent change and band, top flags, approve and reject) plus expandable panels (evidence refs and cited values per flag, specialist summaries, critic verdict, comp and prior-rent context, draft message). BLOCKED cards show the critic reason and no draft.
- **No eval page in the app.** Baseline against multi-agent comparisons live in MLflow and `docs/eval-plan.md`.

## Alternatives considered

- **Databricks App with Lakebase from the start.** Not chosen for the first release, which runs locally. It is the target (ADR-026, ADR-027).
- **Markdown briefs only.** Rejected. No approval capture, so no auditable decision record.

## Consequences

**Benefits**

- Runs locally in Docker Compose.
- Append-only events give a full decision history with no updates in place.
- The repository interface allows a later move to Lakebase with no UI change.

**Costs we accept**

- SQLite is single-user. Concurrent reviewers are not supported.
- Reviewers cannot correct a recommendation, only reject it.

## Revisit when

- Multiple or concurrent reviewers are needed.
- An in-app eval view is wanted.
- An edit path is needed.

## Known gaps and open questions

- Databricks Apps and Lakebase limits on Free Edition are not confirmed (DD-06).
