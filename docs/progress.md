# Progress

Status: living log. Last updated 2026-10-02.
Roadmap: implementation plan (not yet tracked). Phases, milestones, and task ids below follow it.

## Rules
- Log entries are append-only and dated
- Edit only the current position block and milestone rows, and only when a phase or milestone changes
- Each entry names the task id it advances

## Current position
- Phase: P0, architecture docs. ADR index and ADR-001 to ADR-010 merged 2026-10-02 (PR #3, PR #4)
- Next milestone: M0, architecture exit checklist passed
- Active task: 0.1, ADRs
- Next step: on `docs/adrs-011-020` (this state save is its first commit), write ADR-011 to ADR-015, then ADR-016 to ADR-020. Two PRs to stay under about 400 lines. Then ADR-021 to ADR-028 plus `docs/open-decisions.md`
- Resume prompt: "Read AGENTS.md and docs/progress.md. Continue from the next step above. ADRs follow the conventions in docs/decisions/README.md, and each written ADR is linked in its index row. Every PR follows .github/pull_request_template.md. Use bullets, keep outputs succinct, and avoid em dashes."

## Milestones

| Milestone | Exit criteria | Status | Date | Tag |
|---|---|---|---|---|
| M0 | Architecture exit checklist passed | open | | m0 |
| M1 | Contracts tagged, tests green, mini fixture loads end to end | open | | m1 |
| M2a | Harness scores the oracle perfectly and the null agent as expected on the mini fixture | open | | m2a |
| M2b | Full dataset reproducible from a seed, validator passes, keys isolated, identical-redaction test passes | open | | m2b |
| M3 | Baseline scores recorded. DD-02, DD-03, DD-08 closed | open | | m3 |
| M4 | Score delta versus baseline per agent, span nesting verified (DD-05) | open | | m4 |
| M5 | Compliance trap caught, clean-home false positives measured, extra scenario 5 count reported | open | | m5 |
| M6 | A stranger can run it, full eval reproducible from the snapshot | open | | m6 |

## Log

### 2026-10-02
- Task: pre-P0 repo setup
- Done: repo initialized on `main` with README and `.gitignore`
- Next: root `AGENTS.md`, `.gitattributes`, `.env.example`, then 0.1
- Done: root `AGENTS.md` (agent-neutral, lean; planned docs listed as pointers) and `CLAUDE.md` importing it
- Next: `.gitattributes`, `.env.example`, then 0.1 starting with the ADRs
- Done: `.gitattributes` (union merge for `docs/progress.md`) and `.env.example` (`OPENROUTER_API_KEY` only, fake value)
- Next: 0.1, starting with the ADRs
- Decision: repo is `mbnest/lease-renewal-advisor`, public, MIT license
- Done: `LICENSE`, PR template in `.github/`, repo name and license recorded in README and AGENTS.md
- Done: `main` protected by a ruleset (PR required, squash only, no force push or deletion)
- Next: merge this PR, then 0.1 on `docs/adrs`, starting with the ADRs
- Decision: PR template replaced with the owner's template (summary with risk ratings, requirement, contracts, assumptions, dependencies, evidence, signoffs). Every PR follows it
- Gap: risk and rigor rubric not written yet
- Done: PR #1 merged (squash) with the full template
- Proposed (not yet confirmed): ADR plan for 0.1
  - Scope is 28 ADRs. 0011 is the platform principle, 0021 to 0027 cover one substitution each, 0028 is the cost envelope (DD-08)
  - Path `docs/decisions/NNNN-slug.md`. Status "accepted (design only, not built)"
  - Three PRs under about 400 lines each: index and 0001 to 0010; 0011 to 0020; 0021 to 0028 plus `docs/open-decisions.md`
- Decision: ADR plan confirmed, with changes. Three-digit numbers (`NNN-slug.md`) in `docs/decisions/`. `docs/decisions/README.md` is the index, with a one-line summary per ADR. Unwritten ADRs are listed as planned and link once they land
- Done: `docs/decisions/README.md` index (001 to 010 linked, 011 to 028 planned)
- Decision: ADR format. Files `ADR-NNN-slug.md`, title states the decision, header table (status, date, related, pending), sections context, decision, alternatives considered, consequences, revisit when, known gaps
- Done: ADR-001 (orchestration) in the new format, index updated
- Done: AGENTS.md and progress.md limited to tracked sources
- Done: ADR-002 to ADR-010, index titles updated
- Decision: split into two PRs to stay under about 400 lines. PR A: index, ADR-001 to ADR-005, AGENTS.md and progress cleanup. PR B, stacked on A: ADR-006 to ADR-010
- Done: ADR-006 to ADR-010 on `docs/adrs-006-010`, index links them
- Done: PR #3 merged (index, ADR-001 to ADR-005, cleanup). https://github.com/mbnest/lease-renewal-advisor/pull/3
- Done: PR #4 rebased onto `main` after #3, then merged (ADR-006 to ADR-010). https://github.com/mbnest/lease-renewal-advisor/pull/4
- Done: `docs/adrs` and `docs/adrs-006-010` deleted, local and remote
- Gap: auto-delete of merged branches is off. Stacked PRs need a manual rebase and retarget after the lower PR merges
- Next: ADR-011 to ADR-015 on `docs/adrs-011-020`
- Done: ADR-011 to ADR-015 on `docs/adrs-011-020`, index links them
- Next: PR for ADR-011 to ADR-015, then ADR-016 to ADR-020
- Done: PR #5 merged (ADR-011 to ADR-015). https://github.com/mbnest/lease-renewal-advisor/pull/5
- Done: ADR-016 to ADR-020 on `docs/adrs-016-020`, index links them
- Next: PR for ADR-016 to ADR-020, then ADR-021 to ADR-028 plus `docs/open-decisions.md`
- Done: PR #6 merged (ADR-016 to ADR-020). https://github.com/mbnest/lease-renewal-advisor/pull/6
- Decision: ADR-021 to ADR-028 split into two PRs to stay under about 400 lines. PR A: ADR-021 to ADR-024. PR B: ADR-025 to ADR-028 plus `docs/open-decisions.md`
- Done: ADR-021 to ADR-024 on `docs/adrs-021-024`, index links them
- Next: PR for ADR-021 to ADR-024, then ADR-025 to ADR-028 plus `docs/open-decisions.md`

## Known gaps and open questions
- Pinned Python version and folder layout are open
- Link to the tracked implementation plan once it is written
