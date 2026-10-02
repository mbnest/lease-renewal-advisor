# Progress

Status: living log. Last updated 2026-10-02.
Roadmap: implementation plan (draft in `docs/reference/`, untracked). Phases, milestones, and task ids below follow it.

## Rules
- Log entries are append-only and dated
- Edit only the current position block and milestone rows, and only when a phase or milestone changes
- Each entry names the task id it advances
- Drafts in `docs/reference/` stay drafts. Tracked docs are written from them, not copied

## Current position
- Phase: pre-P0 repo setup done. PR #1 merged 2026-10-02 (https://github.com/mbnest/lease-renewal-advisor/pull/1)
- Next milestone: M0, architecture exit checklist passed
- Active task: none
- Next step: on `docs/adrs` (state save is its first commit), start 0.1 with the ADR index and ADRs 0001 to 0010 (plan in the 2026-10-02 log)
- Resume prompt: "Read AGENTS.md and docs/progress.md. Inputs are in docs/reference/ (untracked drafts; session 5 wins on conflicts). Continue from the next step above. Every PR follows .github/pull_request_template.md. Use bullets, keep outputs succinct, and avoid em dashes."

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
- Done: reference inputs complete in `docs/reference/` (scoping doc, addenda 2 to 5, session 4 drafts, ADRs 0001 to 0020, schemas, `policy_v1.yaml`, planning drafts)
- Decision: `docs/reference/` stays untracked, input only
- Decision: drafts are not copied wholesale. Each tracked doc is written when needed, informed by its draft
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
- Gap: risk and rigor rubric not written yet. The draft pointed to a missing `docs/Testing.md` section 8 and a `just packet` command, both dropped
- Done: PR #1 merged (squash) with the full template
- Proposed (not yet confirmed): ADR plan for 0.1
  - Scope is 28 ADRs. 0011 split into 0011 (principle) and 0021 to 0027 (per substitution, session 2 format). 0028 is cost envelope (DD-08). 0021 to 0028 have no drafts
  - Write each ADR from its addendum source. Session 1 addendum lives inside the scoping doc. Draft ADRs are cross-checks only
  - Cite addenda by name. The ADR index states the addenda are private planning notes, not in the repo
  - Path `docs/decisions/NNNN-slug.md`. Status "accepted (design only, not built)"
  - Three PRs under about 400 lines each: index and 0001 to 0010; 0011 to 0020; 0021 to 0028 plus `docs/open-decisions.md`
  - Fix the stale 0017 index title (one gateway, OpenRouter)

## Known gaps and open questions
- Pinned Python version and folder layout are open
- Link to the tracked implementation plan once it is written
