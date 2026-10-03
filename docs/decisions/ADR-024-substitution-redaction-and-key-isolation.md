# ADR-024: Redact and isolate keys in a Python access layer for release one, UC controls as the target

| | |
|---|---|
| **Status** | Accepted (design only, not built) |
| **Date** | 2026-10-02 |
| **Last updated** | 2026-10-03 |
| **Related** | ADR-005 (MCP server), ADR-008 (tracing), ADR-010 (guardrails), ADR-013 (ground truth), ADR-021 (storage), ADR-022 (tool access) |
| **Pending** | None |

## Context

Protected-characteristic fields must be redacted before any model, span, or trace sees them ([ADR-010](ADR-010-guardrails-tiering-and-audit-record.md)). Answer keys must stay outside the agent-readable data path, or grading is invalid ([ADR-013](ADR-013-ground-truth-and-compliance-trap.md)).

Both rules must hold on every backend, and a backend swap must not weaken them.

## Decision

**Release one enforces redaction in the Python access layer and isolates keys with a directory allowlist. The target uses UC views or column masks and a restricted key schema. The redaction interface is the seam.**

| | |
|---|---|
| Target | UC views or column masks for protected fields. Answer keys in a separate, restricted schema |
| Release one | Python access layer redacts protected fields. Agents read only from allowlisted directories, and keys live outside them |
| Seam | Redaction interface, plus an identical-output test |

**Preserved by the stand-in**

- The same redacted fields and the same redacted output for every access function.
- No agent, tool, span, or trace receives an unredacted protected field ([ADR-008](ADR-008-mlflow-tracing-behind-own-decorator.md)).
- Keys unreachable from any agent-readable path.

**Not preserved**

- Enforcement by the platform. The Python layer is enforced by code and tests, so a code change could bypass it.
- UC grants on the key schema, and audit of who read it.

**Identical-redaction test:** when the Databricks backend exists, both layers must produce identical redacted output for the same inputs. The Python layer stays primary until the test passes.

## Alternatives considered

- **Platform controls only.** Rejected for release one. No workspace, and local runs would have no redaction.

## Consequences

**Benefits**

- Redaction holds from the first local run, before any platform work.
- The identical-redaction test makes the swap checkable.

**Costs we accept**

- Two layers to keep in sync once the target exists.
- The allowlist is weaker than schema permissions until the Databricks phase.

## Revisit when

- The Databricks backend is built. The identical-redaction test is the first seam to validate ([ADR-011](ADR-011-databricks-target-local-first-release.md)).

## Known gaps and open questions

- The list of protected fields is set with the schemas (after M0).
- Whether views or column masks fit better is not decided.
