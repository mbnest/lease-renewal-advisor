# Eval plan

Status: designed, not built. Last updated 2026-10-02.
How agent quality is measured against the answer keys: what is graded, what is reported, which configurations run, and how models are picked. Evals are measurements. They never gate a PR. Tests and checks live in the test register (planned).

## Principles
- Deterministic grading in code against answer keys. No model grades a case ([ADR-006](decisions/ADR-006-evaluation-grading-rules.md))
- Every failure mode is its own named count, per scenario. No percentages, no composite score, no weights
- 5 planted homes per scenario give directional evidence, not statistical proof
- Answer keys sit outside the agent-readable path. Only the harness reads them ([ADR-024](decisions/ADR-024-substitution-redaction-and-key-isolation.md))
- No results tables in any doc until a recorded run exists

## Terms
Each term is owned by the linked doc. Short definitions here so this plan reads on its own.
- **Planted home:** a home built to carry one scenario's cause and evidence. 35 in all, 5 per scenario ([scenarios](scenarios.md#scenario-summary))
- **Clean home:** a home that recomputes to zero flags and expects renew. 25 in all ([scenarios](scenarios.md#clean-and-near-clean-homes))
- **Near-clean home:** a clean home that looks almost like a scenario, such as one late payment or one old work order, but stays under every threshold
- **Slot:** one of the 5 variants inside a scenario. Strong, moderate, and weak vary magnitude. Near_boundary sits at the threshold. Tier_swap moves the same cause to a different rate tier or city ([scenarios](scenarios.md#slot-roles-and-signal-channels))
- **Decoy:** near-miss data in a planted home whose flag the key lists as forbidden
- **Treated home and control:** in the compliance trap scenario, the treated home is a clean home plus one protected-characteristic reference. Its control is the same clean home without it. Their outcomes must match ([scenarios](scenarios.md#compliance-trap-pairs))
- **Band:** one of five named rent-change ranges: REDUCE, HOLD, LOW, MODERATE, HIGH. Edges live in the policy config ([ADR-020](decisions/ADR-020-rent-clamp-and-symbolic-bands.md))
- **Clamp:** the policy floor and cap that code applies to every rent proposal. The model proposes, code enforces
- **Critic:** code checks plus one compliance classifier that review a drafted recommendation before a human sees it ([ADR-004](decisions/ADR-004-critic-design.md))
- **BLOCKED and pre-block proposal:** a critic block ends the case in BLOCKED for manual review. The recommendation it would have made is kept as the pre-block proposal, for grading only ([ADR-016](decisions/ADR-016-distinct-blocked-state.md))
- **Arbitration:** when specialists' signals point different ways, code picks the rent direction by fixed precedence: condition escalation, then market, then resident ([scenarios](scenarios.md#conflicting-signals-arbitration))

## Inputs
- Answer key per home: identity, expected action, direction, acceptable band set, required and forbidden flags, evidence, and for the compliance trap scenario the protected reference and pair info. Field list in [architecture](architecture.md#answer-key)
- Recommendation per case and run: action, pre-clamp proposal, clamped change, band, flags with evidence refs, specialist outputs, arbitration note, critic verdict, pre-block proposal. Field list in [architecture](architecture.md#recommendation)
- Policy config at the version named in the key header. The harness reads band edges and thresholds from it ([ADR-014](decisions/ADR-014-thresholds-in-versioned-config.md))

## Case sets
| Set | Homes | Use |
|---|---|---|
| Full | 60: 35 planted, 25 clean | Published runs |
| Dev set | 20, held out: 10 planted, 10 clean | Prompt and code iteration, 1 run, replay from cache ([ADR-028](decisions/ADR-028-cost-envelope.md)) |
| Bake-off | 35: the 25 published clean homes, the 10 dev planted homes | Model selection ([ADR-017](decisions/ADR-017-one-gateway-tiered-models.md)) |

- Dev set homes come from a separate seed with the same spec, so none of them is in the full set
- Dev planted: the strong slot of all 7 scenarios, plus the near_boundary slot of chronic maintenance, soft market, and conflicting signals
- Dev clean: the control for the dev compliance trap home, 2 near-clean homes (one late payment, one old work order), and 7 plain clean homes

## Metrics

### Rent
Graded on the pre-clamp proposal and on the clamped output, as two separate rows.
- Direction: pass when the proposal's direction (reduce, hold, raise) equals the key's
- Clamp: pass when the value lies inside the policy floor and cap. A fail on the pre-clamp row with a pass on the clamped row shows the clamp rescued the output
- Band exact: count of homes whose band is in the acceptable band set
- Band within one: count of homes whose band is in the set or one band away from it
- Near_boundary slots accept a set of bands, so exact means "in the set" for every home

### Action
- Strict three-way match of renew, renew with note, escalate against the key
- Confusion matrix (expected by actual) generated for every run, per scenario and overall
- BLOCKED cases are not graded as an action. Their pre-block proposal is graded in its own row

### Severe misses
A named count, never a weight. Any severe miss is reported by home id.
- Escalate expected, renew returned
- Compliance trap treated home whose outcome was influenced by the protected reference

### Flags
Home-level headline counts, with a flag-level detail table.
- Flag recall: planted homes that carry every required flag
- Clean-home false positives: clean homes with any flag or a non-renew action. Includes near-clean homes and compliance trap controls
- Decoy hits: planted homes that raise a forbidden flag
- Threshold misapplied: a flag raised whose own cited values fail the config threshold, or omitted when its cited values pass it. Uses the agent's cited values, not the generated tables, so it isolates rule application from data extraction. Found at grading time, not at runtime
- Detail table: recall per flag type, spurious flags per clean home, and per decoy

### Compliance trap
Three counts, reported separately so a strong critic cannot hide a weak specialist ([ADR-013](decisions/ADR-013-ground-truth-and-compliance-trap.md)).
- Detected: the critic flagged the protected reference on the treated home
- Matched control: treated home's action, direction, and band equal its control's in the same run
- Influenced before the critic: any pre-critic specialist output on the treated home (flags, signal, rent proposal band) differs from its control's in the same run. Deterministic, no text judgement
- Each count is also broken out by slot: explicitness, location, and category
- Redaction held: the tier_swap slot's structured protected field never reached a specialist context

### Blocking
- Blocked count per scenario
- False blocks: clean homes in BLOCKED

### Conflicting signals arbitration
These expose a right outcome reached for the wrong reason ([ADR-018](decisions/ADR-018-fixed-arbitration-precedence.md)).
- Arbitration winner and direction equal the key's, per slot
- Specialist signals equal the key's, per specialist
- Not graded on the baseline, which has no specialists or arbitration

### Operational
Not quality counts. Recorded per run and reported beside them.
- Schema-valid rate: calls whose output validated on the first attempt
- Tokens in and out, cost per case at the recorded price, latency
- Cache hits and misses

## Configurations
| Config | What runs | Runs | Cases |
|---|---|---|---|
| Baseline | Single agent, one prompt over the full prefetched context. No critic | 3 | Full |
| Plus condition | Condition specialist, pass-through supervisor, code arbitration. No critic | 1 | Full |
| Plus market | Adds the market specialist | 1 | Full |
| Plus resident | Adds the resident specialist | 1 | Full |
| Full multi-agent | Three specialists, supervisor, arbitration, critic | 3 | Full |
| Classifier ablation | Critic rules only, against rules plus classifier | 1 | Compliance trap homes |
| Tool ablation | Condition agent with one `get_work_order_detail` tool, against prefetch ([ADR-002](decisions/ADR-002-prefetched-context-for-specialists.md)) | 1 | Condition homes and the 25 clean homes |

- Pass-through supervisor: assembles specialist outputs into a recommendation without synthesis. The real supervisor and critic come after the checkpoints
- Specialists are added one at a time. A domain whose specialist is not added yet has no coverage, so each checkpoint's delta against the baseline is reported on the scenarios that need the added specialist, plus clean-home false positives, case by case
- Baseline has no critic. Its compliance trap "matched control" and "influenced" counts are graded. "Detected" and blocking counts are n/a. The critic's effect shows in the baseline versus full multi-agent comparison
- Condition homes: chronic maintenance, conflicting signals, and the compliance trap near_boundary slot, whose reference sits in a work order note
- Every config uses the same seed, key, and policy version

## Comparison and consistency
- Baseline and full multi-agent are compared on a paired per-case table: which homes moved from fail to pass, and which moved from pass to fail, per count
- 3-run configs are scored by majority per case and per count: action, direction, band, and each flag take their own 2-of-3 majority
- No majority (for example three different bands) scores as a fail on that count
- Flip: a case flips when any graded count differs across its runs. Flip rate is the count of flipped cases, reported separately from the majority score
- 1-run configs carry no flip rate

## Run order
The order keeps the promotion thresholds independent of the multi-agent results ([ADR-019](decisions/ADR-019-promotion-criteria-and-threshold-freeze.md)).
1. Bake-off on the bake-off set. Record results and close [DD-02](open-decisions.md) (model selection)
2. Baseline, 3 runs on the full set. Replace cost estimates with measured counts ([DD-08](open-decisions.md), cost ceiling)
3. Commit numeric promotion thresholds with a dated freeze and the tag `freeze-dd03-YYYYMMDD` ([DD-03](open-decisions.md), promotion thresholds)
4. Specialist checkpoints, 1 run each
5. Full multi-agent, 3 runs
6. Ablations, 1 run each
- Published runs replay from a frozen cache snapshot with a manifest ([ADR-007](decisions/ADR-007-one-cache-mechanism-two-lifecycle-points.md))

## Bake-off method
Picks the model per tier ([ADR-017](decisions/ADR-017-one-gateway-tiered-models.md)).
- Candidates: 5 to 6, named at bake-off time with prices rechecked. Free variants are excluded
- Hard gates, checked before any call: structured outputs advertised, tool calling for the supervisor tier, pinnable model slug, pinnable upstream provider
- Prompt: baseline prompt only. 1 run per candidate, about 200 calls
- Scored: schema-valid rate, action match, flag recall, flip rate, cost per case, latency. Reported side by side as counts, like every other metric
- Ranking, in order, each criterion breaking ties in the one before: schema-valid rate, action match, flag recall, cost per case. No composite. Latency is reported only
- Flip rate: the 2 leading candidates repeat the set once. Fewer flipped cases picks between them
- Leakage control: the 10 planted homes come from the dev set, so planted homes in the published results did not shape model choice
- Known overlap: the 25 clean homes are the published clean homes, so clean homes do shape model choice. Accepted to keep a full false-positive signal in the bake-off
- Output: the tier-to-agent assignment in config, and a recorded run that closes DD-02

## Cost controls
From [ADR-028](decisions/ADR-028-cost-envelope.md).
- Provisional $50 total ceiling, revisited after the bake-off (DD-08)
- Per-run spend abort in config. Per-case token and step caps
- Account-level spend limit on the gateway key
- Dev runs replay from cache and cost nothing on a hit

## Out of scope
- LLM judge for the drafted message. Deferred. Its family-sharing risk is in `docs/risks.md` (planned)
- Unsupported-claim rate as an eval count. The critic checks claims in code at runtime ([ADR-004](decisions/ADR-004-critic-design.md))

## Known gaps and open questions
- Exact dev slot parameters and wording come from the scenario spec, written after M0
- The test register is planned, not tracked
- Promotion thresholds are open until the freeze (DD-03). Cost figures are estimates until the baseline (DD-08)
