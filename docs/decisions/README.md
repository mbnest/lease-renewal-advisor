# Architecture decision records

Status: living index. Last updated 2026-10-02.
Index of every ADR, with a one-line summary of each decision.

## Conventions
- File name: `ADR-NNN-slug.md`, three-digit number, never reused
- Title: the decision, stated as an action
- Header table: status, date, related ADRs, pending DD-nn items
- Sections: context, decision, alternatives considered, consequences (benefits, costs we accept), revisit when, known gaps and open questions
- Status: "Accepted (design only, not built)" until code and tests exist
- Rationale is about the project only: its requirements, constraints, and evaluation
- Deferred items (DD-nn) live in `docs/open-decisions.md` (planned)
- A superseded ADR stays in place, marked superseded, with a link to its replacement

## Index

### Agents and orchestration
| ADR | Title | Decision | Status |
|---|---|---|---|
| [ADR-001](ADR-001-plain-python-asyncio-orchestration.md) | Orchestrate agents in plain Python with asyncio | Hand-coded asyncio flow with Pydantic contracts. No agent framework, no Agent Bricks | accepted |
| [ADR-002](ADR-002-prefetched-context-for-specialists.md) | Prefetch specialist context in code | Code prefetches each specialist's evidence. One narrow tool is tested only as an ablation | accepted |
| [ADR-003](ADR-003-economics-and-critic-logic-stay-code.md) | Keep economics and critic logic in code | Rent economics is a code tool the supervisor calls. LLM agents are only the supervisor and three specialists | accepted |
| [ADR-004](ADR-004-critic-design.md) | Verify claims in code and check compliance with rules plus one classifier | Code verifies every cited claim. Keyword rules plus one narrow classifier check compliance | accepted |
| [ADR-005](ADR-005-custom-thin-mcp-server.md) | Start tool access with a thin custom MCP server | Custom MCP server over the Python access functions, added after evals are measurable | accepted |

### Evaluation and observability
| ADR | Title | Decision | Status |
|---|---|---|---|
| [ADR-006](ADR-006-evaluation-grading-rules.md) | Grade with separate named counts, not a composite score | Pass/fail on direction and clamp, strict three-way action match, severe misses counted separately | accepted |
| [ADR-007](ADR-007-one-cache-mechanism-two-lifecycle-points.md) | Use one cache for development and published results | Hash-keyed call cache for dev, frozen snapshot with manifest for published runs | accepted |
| [ADR-008](ADR-008-mlflow-tracing-behind-own-decorator.md) | Trace through the project's own decorator over MLflow | Agent code uses a thin `@traced` decorator. Only it imports MLflow | accepted |

### Reviewer experience and guardrails
| ADR | Title | Decision | Status |
|---|---|---|---|
| [ADR-009](ADR-009-streamlit-reviewer-ui-and-sqlite-state.md) | Review in Streamlit with append-only SQLite state | Streamlit approval page, card, and dashboard. Append-only SQLite decision events | accepted |
| [ADR-010](ADR-010-guardrails-tiering-and-audit-record.md) | Enforce guardrails in code, with an approval gate and an audit record | No send or write capability. Code-enforced approval gate. Minimal audit record per recommendation | accepted |

### Platform layer
| ADR | Title | Decision | Status |
|---|---|---|---|
| [ADR-011](ADR-011-databricks-target-local-first-release.md) | Design for a Databricks target, release locally first | Docs describe the Databricks Free Edition target. Release one is local, every stand-in behind a seam | accepted |
| [ADR-021](ADR-021-substitution-storage.md) | Store data in Parquet for release one, Delta in Unity Catalog as the target | Delta in Unity Catalog, stood in by Parquet behind the data-access interface | accepted |
| [ADR-022](ADR-022-substitution-tool-access.md) | Serve tools from a custom thin MCP server for release one, managed UC Functions MCP as the target | Managed UC Functions MCP, stood in by the custom thin MCP server | accepted |
| [ADR-023](ADR-023-substitution-data-prep.md) | Prepare data with a seeded Python generator for release one, a Databricks pipeline as the target | Pipeline on Databricks, stood in by the seeded Python generator | accepted |
| [ADR-024](ADR-024-substitution-redaction-and-key-isolation.md) | Redact and isolate keys in a Python access layer for release one, UC controls as the target | UC views or column masks, stood in by the Python access layer and a directory allowlist | accepted |
| ADR-025 | Substitution: observability | Databricks-managed MLflow, stood in by local MLflow in Docker | planned |
| ADR-026 | Substitution: approval and audit state | Lakebase, stood in by SQLite behind the repository interface | planned |
| ADR-027 | Substitution: reviewer UI | Streamlit as a Databricks App, stood in by Streamlit in Docker Compose | planned |

### Data and ground truth
| ADR | Title | Decision | Status |
|---|---|---|---|
| [ADR-012](ADR-012-data-scale-scenarios-and-variants.md) | Generate 60 homes across 7 scenarios with seeded variant slots | 7 scenarios, 60 homes (35 planted, 25 clean), seeded variant slots | accepted |
| [ADR-013](ADR-013-ground-truth-and-compliance-trap.md) | Build ground truth by construction and test the compliance trap with paired controls | Hand-authored keys checked by a generation-time validator. Counterfactual pairs for the protected reference | accepted |

### Policy and decision logic
| ADR | Title | Decision | Status |
|---|---|---|---|
| [ADR-014](ADR-014-thresholds-in-versioned-config.md) | Keep policy thresholds in versioned config, with no runtime recompute | Agents see a versioned policy config. No runtime recompute by the critic | accepted |
| [ADR-015](ADR-015-action-definitions-with-severity-tags.md) | Define actions semantically, with severity tags in config | Semantic action definitions. Severity tags in config. Highest severity wins | accepted |
| [ADR-016](ADR-016-distinct-blocked-state.md) | Send critic blocks to a distinct BLOCKED state | Critic blocks go to a terminal BLOCKED state and a manual-review queue, counted separately | accepted |
| [ADR-017](ADR-017-one-gateway-tiered-models.md) | Route all model calls through one gateway, with tiered models | OpenRouter as the single gateway. Smaller models for specialists, larger for supervisor and classifier | accepted |
| [ADR-018](ADR-018-fixed-arbitration-precedence.md) | Resolve specialist conflicts with a fixed precedence list | Specialist conflicts resolved by a fixed precedence list in config. Code decides, model explains | accepted |
| [ADR-019](ADR-019-promotion-criteria-and-threshold-freeze.md) | Fix promotion non-negotiables now, freeze numeric thresholds after baseline | Non-negotiables fixed now. Numeric thresholds frozen after baseline, before multi-agent results | accepted |
| [ADR-020](ADR-020-rent-clamp-and-symbolic-bands.md) | Clamp rent changes globally and grade against symbolic bands | Global floor and cap clamp. Five named bands resolved by the policy config | accepted |
| ADR-028 | Cost envelope | Lean run plan, provisional $50 ceiling, per-run spend abort | planned |

## Known gaps and open questions
- ADRs 025 to 028 are not written yet. Rows link once each file lands
- `docs/open-decisions.md` is not written yet
