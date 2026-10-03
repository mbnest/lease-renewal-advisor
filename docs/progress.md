# Progress

Status: living index. Last updated 2026-10-03.
Where the project stands and where to resume. Detail lives in one log per milestone under `docs/progress/`. Roadmap: implementation plan (not yet tracked). Phases, milestones, and task ids follow it.

## Current position
- Phase: P0, architecture docs. All 28 ADRs, `docs/open-decisions.md`, and `docs/architecture.md` merged 2026-10-02 (PR #3 to PR #9). `docs/scenarios.md` merged (PR #10). `docs/eval-plan.md` merged (PR #11). `docs/risks.md` merged (PR #12). README refresh in review on `docs/readme`
- Next milestone: M0, architecture exit checklist passed. Checklist in [docs/progress/m0.md](progress/m0.md)
- Active task: 0.1, architecture docs
- Next step: owner reviews and merges the README PR. Then one review pass against the M0 checklist. DD-04 calibration (sourced rent ranges for the clamp and city rate tiers) is still open
- Resume prompt: "Read AGENTS.md and docs/progress.md, then the current milestone log. Continue from the next step above. Docs state decisions already made in the ADRs and link to them, and log missing decisions as gaps rather than inventing them. Every PR follows .github/pull_request_template.md. Use bullets, keep outputs succinct, and avoid em dashes."

## Milestones

| Milestone | Exit criteria | Status | Date | Tag | Log |
|---|---|---|---|---|---|
| M0 | Architecture exit checklist passed | open | | m0 | [m0](progress/m0.md) |
| M1 | Contracts tagged, tests green, mini fixture loads end to end | open | | m1 | |
| M2a | Harness scores the oracle perfectly and the null agent as expected on the mini fixture | open | | m2a | |
| M2b | Full dataset reproducible from a seed, validator passes, keys isolated, identical-redaction test passes | open | | m2b | |
| M3 | Baseline scores recorded. DD-02, DD-03, DD-08 closed | open | | m3 | |
| M4 | Score delta versus baseline per agent, span nesting verified (DD-05) | open | | m4 | |
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
- Pinned Python version and folder layout are open
- Link to the tracked implementation plan once it is written
