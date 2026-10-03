# AGENTS.md

Status: living rules. Last updated 2026-10-03.
Rules for every coding agent (Claude Code, Codex, others) and human contributor.

## Project
- Lease renewal decision agent: multi-agent, advisory, synthetic data, graded against answer keys
- Phase: architecture. Everything is designed, not built, until a commit says otherwise
- Overview: [README.md](README.md)
- Repo: `mbnest/lease-renewal-advisor` on GitHub, public, MIT license
- Current state, next step, and resume prompt: [docs/progress.md](docs/progress.md). Read it first, then the current milestone log it links

## Writing style
- Succinct. Bullets. Sentence case headings. Exception: the README title is the project name in title case, "Lease Renewal Decision Agent"
- No em dashes anywhere, docs included. Use plain sentence breaks
- No emojis in code, docs, or commits
- Each doc starts with a status line and last-updated date, and ends with a known gaps and open questions section
- Docs are self-descriptive. Name things, never bare numbers: scenarios by name (for example "conflicting signals"). ADR and DD ids are fine when linked
- Define a term briefly where it is used and link to the doc that owns its definition or scope

## Working method
- Keep it simple. Do not overengineer or program defensively
- Work in small increments. Validate each one before moving on
- Find and prove the root cause before fixing. No workarounds
- If a decision is missing or conflicting, do not invent one. Log it under known gaps and in the current milestone log
- Use current APIs

## Code style
- Python package manager is uv. Use `uv run` and `uv add`. Never `python3` directly or `pip install`
- Python 3.13, pinned in `.python-version`
- Short modules and functions, named clearly
- Clear, concise docstrings. Sparing comments elsewhere
- Exception handling only where needed

## Folder layout
Directories are created by the first PR that needs them. Each lane edits only its own.

| Path | Holds | Lane |
|---|---|---|
| `src/lease_renewal/generator/` | Seeded generator, validator, key writer | a |
| `schemas/` | JSON schemas for contracts | a, via `contract/` branches |
| `config/` | Policy config and scenario spec | a |
| `src/lease_renewal/eval/` | Harness, grading, run manifests | b |
| `src/lease_renewal/infra/` | Access layer, redaction, tracing, cache | b |
| `src/lease_renewal/decision/` | Policy resolution, clamp, economics, arbitration | c |
| `src/lease_renewal/critic/` | Claim checks, keyword rules, classifier flow | c |
| `src/lease_renewal/state/` | Gate, approval events, audit snapshot | d |
| `src/lease_renewal/ui/` | Streamlit reviewer UI | d |
| `src/lease_renewal/agents/` | Baseline, specialists, supervisor | e |
| `src/lease_renewal/prompts/` | Prompt files | e |
| `tests/` | Tests, mirroring `src/lease_renewal/` | owner of the code under test |
| `docs/`, `README.md` | Docs | f |

- Paths for generated data and the restricted answer-key directory are set with the access layer ([ADR-024](docs/decisions/ADR-024-substitution-redaction-and-key-isolation.md))

## Phase rules
- No logic code and no schemas until the architecture exit checklist passes (milestone M0)
- Do not claim anything is built, tested, or evaluated unless a test or a recorded run shows it
- No results tables until real eval numbers exist
- Target Databricks components are "designed, not validated"

## Safety and design rules (carry into code)
- The system has no send or write capability. It only recommends and records
- Protected-characteristic fields are redacted in the data layer before any model, span, or trace sees them
- Answer keys live outside the agent-readable data path
- Model proposes, code enforces: rent clamp, arbitration, and gate states are code
- Every agent returns schema-validated JSON. Cap steps and tokens per case. Low temperature

## Secrets and data hygiene
- Never commit keys, tokens, or credentials. Keep them in `.env`, which is gitignored
- Do not read, print, or echo `.env` contents. Keep secrets out of code, docs, PR text, logs, traces, and manifests
- If a key leaks, rotate it. Deleting the commit is not enough
- All data is synthetic. Never add real names, addresses, resident messages, or other real personal data

## Git
- `main` is protected. Merge through pull requests, squash merge
- Branch names: `<lane>/<wbs-id>-<slug>`, `contract/<slug>`, `docs/<slug>`, `eval/<run-id>`
- Commit format: `<lane>(<wbs-id>): <summary>`, for example `f(0.1): add progress log`
- Commit messages never reference a coding agent. No agent names, no Co-Authored-By or "generated with" trailers
- Lanes: a data and keys, b eval and infra, c decision code, d state and UI, e agents, f docs and process
- Keep PRs small, under about 400 changed lines
- Every PR description follows `.github/pull_request_template.md`. Fill every section. Write "None" or "n/a" rather than deleting one
- Evidence is pasted check or test output, never hand-edited

## Upkeep
- Log decisions, gaps, deviations, and PR links in the current milestone log under `docs/progress/`: append-only, dated, naming the task id. `docs/progress.md` is the index and follows its own rules
- Update the README status table in the same commit that changes a component's state
- Deferred decisions (DD-nn) live in [docs/open-decisions.md](docs/open-decisions.md). Close an item by updating its row, the affected ADR, and the status table in the same commit
- ADRs live in `docs/decisions/`. Follow the format and index rules in `docs/decisions/README.md`

## Planned (rules expand when these land)
- Branching and lane ownership in `docs/branching-strategy.md`
- Test register and CI rules in `docs/testing-strategy.md`. No live model calls in CI

## Known gaps and open questions
- PR template risk ratings (reach, reversibility, exposure, detection) and rigor tiers have no written rubric yet
