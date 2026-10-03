# Progress

Status: living index. Last updated 2026-10-03.
Where the project stands and where to resume. Detail lives in one log per milestone under `docs/progress/`. Roadmap: implementation plan (not yet tracked). Phases, milestones, and task ids follow it.

## Current position
- Phase: P1, foundations. M0 closed 2026-10-03, tag `m0` (PR #15). P0 history: all 28 ADRs, `docs/open-decisions.md`, and `docs/architecture.md` merged 2026-10-02 (PR #3 to PR #9). `docs/scenarios.md` merged (PR #10). `docs/eval-plan.md` merged (PR #11). `docs/risks.md` merged (PR #12). README refresh, Python pin, folder layout, and security policy merged (PR #13). [DD-04](open-decisions.md) calibration decided and merged (PR #14)
- Next milestone: M1, contracts tagged, tests green, mini fixture loads end to end. Checklist in [docs/progress/m1.md](progress/m1.md)
- Active task: none. Task 1.1 merged (PR #16). Task 1.5, the agent spike, is complete and its branch `e/1.5-agent-spike` is throwaway, so no spike code is on `main`
- Next step: scope task 1.2 and commit the contracts. Carry these spike lessons into it: derive acceptable directions from the acceptable band set rather than authoring a separate direction field, give the harness per-flow metric applicability, and record `finish_reason` and reasoning tokens per call. Findings: [M1 log, step 1](progress/m1.md#2026-10-03-task-15-step-1-findings), [correction](progress/m1.md#2026-10-03-task-15-step-1-correction), [step 2](progress/m1.md#2026-10-03-task-15-step-2-findings)
- Resume prompt: "Read AGENTS.md and docs/progress.md, then the current milestone log. Continue from the next step above. Docs state decisions already made in the ADRs and link to them, and log missing decisions as gaps rather than inventing them. Every PR follows .github/pull_request_template.md. Use bullets, keep outputs succinct, and avoid em dashes."

## Milestones

| Milestone | Exit criteria | Status | Date | Tag | Log |
|---|---|---|---|---|---|
| M0 | Architecture exit checklist passed | closed | 2026-10-03 | m0 | [m0](progress/m0.md) |
| M1 | Contracts tagged, tests green, mini fixture loads end to end | open | | m1 | [m1](progress/m1.md) |
| M2a | Harness scores the oracle perfectly and the null agent as expected on the mini fixture | open | | m2a | |
| M2b | Full dataset reproducible from a seed, validator passes, keys isolated, identical-redaction test passes | open | | m2b | |
| M3 | Baseline scores recorded. [DD-02](open-decisions.md), [DD-03](open-decisions.md), [DD-08](open-decisions.md) closed | open | | m3 | |
| M4 | Score delta versus baseline per agent, span nesting verified ([DD-05](open-decisions.md)) | open | | m4 | |
| M5 | Compliance trap caught, clean-home false positives measured, compliance trap influenced-before-critic count reported | open | | m5 | |
| M6 | A stranger can run it, full eval reproducible from the snapshot | open | | m6 | |

## Rules
- This file holds only the current position, the milestone table, and open gaps. No log entries
- Each milestone has one log, `docs/progress/<milestone>.md`, created when work on it starts and linked in the table
- A log holds the milestone's exit checklist and a dated, append-only log. Each entry names its task id
- Log decisions with the reason, gaps found, deviations from the plan, and one PR link per piece of work
- Do not log step-by-step done and next pairs, branch cleanup, or anything git history already records
- A log closes when its milestone is tagged. Set its status line to closed with the date
- Edit the current position when the next step changes. Edit milestone rows only when a milestone changes

## Known gaps and open questions
- Link to the tracked implementation plan once it is written
