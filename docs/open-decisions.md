# Open decisions

Status: living register. Last updated 2026-10-02.
Deferred decisions (DD-nn) and the standing revisit triggers that live in the ADRs.

## Rules
- One row per deferred item. Rows are never deleted. Closing an item sets status to decided or frozen, with the date
- A commit that closes an item updates, in the same commit: this row, the affected ADR (decision text or revisit trigger, and its Pending row), and the README status table if a component's state changes. Log it in `docs/progress.md`
- Every ADR with an open item names it in its Pending row
- Frozen items (DD-03) are committed in the ADR with a dated freeze and a git tag before multi-agent results are viewed

## Deferred decisions

| ID | Item | Why deferred | Gating event | Affects | Status | Date closed |
|---|---|---|---|---|---|---|
| DD-01 | Tuned policy thresholds and severity tags | Values need generated data to check against | First generation run | ADR-014, ADR-015, policy config | open | |
| DD-02 | Model selection and tier-to-agent assignment, including OpenRouter pinning and fallback options | Needs bake-off results and verified gateway options | Baseline bake-off recorded | ADR-007, ADR-017 | open | |
| DD-03 | Numeric promotion thresholds | Needs the baseline. Must be frozen before multi-agent results are viewed | After baseline, before multi-agent results are viewed | ADR-010, ADR-019 | open | |
| DD-04 | Rent clamp and city rate calibration to sourced DFW ranges | Needs sourced ranges. 2026 metro rents are falling | README drafting | ADR-012, ADR-020, README | open | |
| DD-05 | MLflow version pin and span nesting verification | Needs a tracing stub to test against | Tracing stub added | ADR-008, ADR-025 | open | |
| DD-06 | Free Edition feasibility: apps count, Lakebase, managed MCP, managed MLflow, quota. Model serving is an optional seam only | Published limits conflict across doc versions. Needs a real workspace | Start of the Databricks phase | ADR-005, ADR-009, ADR-011, ADR-022, ADR-025, ADR-026, ADR-027 | open | |
| DD-07 | Scenario 8 signal vocabulary | Vocabulary is thin until the scenario spec is written | Scenario spec authoring | ADR-012, ADR-018, scenario spec | open | |
| DD-08 | Cost ceiling and measured per-case cost | Estimates rest on assumed prices and token counts | Bake-off and baseline run | ADR-017, ADR-028 | open | |
| DD-09 | Resolution event disposition vocabulary | Set with the recommendation schema | Recommendation schema authoring | ADR-016, ADR-026 | open | |
| DD-10 | Coding agent task, branch, and environment mechanics | Not exercised until a coding agent runs a task | First coding agent task | Branching strategy (planned), AGENTS.md | open | |
| DD-11 | Single-source task list for the plan and Gantt view | Low priority until the two drift | First drift between them | Implementation plan (not yet tracked) | open | |

## Standing triggers

Revisit conditions that stay open for the life of an ADR. The ADR's "Revisit when" section is authoritative.

| Trigger | ADR |
|---|---|
| Hybrid retrieval: histories outgrow the context, or cases need drill-down | ADR-002 |
| Economics or critic logic moves to an agent | ADR-003 |
| Compliance classifier gaps | ADR-004 |
| Custom MCP server to the managed server | ADR-005 |
| Noisy eval: add homes beyond 60 | ADR-006, ADR-012 |
| Cache staleness: model or provider retired or changed | ADR-007 |
| Audit explainability after a prompt or policy change | ADR-010 |
| Critic recompute of thresholds | ADR-014 |

## Known gaps and open questions
- Milestones per item are not mapped until the implementation plan is tracked
- DD-10 and DD-11 affect documents that are not tracked yet
