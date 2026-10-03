# ADR-027: Run the reviewer UI in Docker Compose for release one, as a Databricks App as the target

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-009 (UI and state), ADR-011 (local-first release), ADR-026 (state substitution) |
| **Pending** | DD-06 (Free Edition feasibility, including apps) |

## Context

The reviewer UI is a Streamlit app: approval page, per-home card, and operational dashboard ([ADR-009](ADR-009-streamlit-reviewer-ui-and-sqlite-state.md)). Streamlit is a supported Databricks Apps framework, so the same app code can run in both places.

## Decision

**Release one runs Streamlit in Docker Compose. The target deploys the same app as a Databricks App. No seam is needed beyond configuration.**

| | |
|---|---|
| Target | Streamlit app deployed as a Databricks App |
| Release one | Streamlit service in Docker Compose, beside MLflow and the eval runner |
| Seam | None. The app reads data and state through the access and repository interfaces |

**Preserved by the stand-in**

- Pages, cards, and the approve and reject flow.
- Every read and write goes through the same interfaces ([ADR-021](ADR-021-substitution-storage.md), [ADR-026](ADR-026-substitution-approval-and-audit-state.md)).

**Not preserved**

- Workspace sign-in and on-behalf-of auth. The local app has no user auth.
- Hosting, availability, and scale.

## Alternatives considered

- **Databricks App from the start.** Not chosen for release one. Needs a workspace, and app limits on Free Edition are unconfirmed.

## Consequences

**Benefits**

- One app codebase for both environments.
- Local review needs only Docker.

**Costs we accept**

- The reviewer identity in decision events is self-reported locally until the target adds sign-in.

## Revisit when

- The Databricks phase starts and app support is confirmed in the workspace ([DD-06](../open-decisions.md)).

## Known gaps and open questions

- Free Edition app count is not confirmed. Doc versions disagree (DD-06).
- How the reviewer is identified in local decision events is not decided.
