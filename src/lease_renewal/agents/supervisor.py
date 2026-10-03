"""Supervisor: combine specialist findings, explain arbitration, draft the message.

Arbitration runs in code before the supervisor and is binding (ADR-018). The
clamp, the band lookup, and the action all stay in code (ADR-003, ADR-015).
"""

import asyncio
import json
from importlib import resources

import httpx

from lease_renewal.agents.gateway import call_json_async
from lease_renewal.agents.multi_schema import SupervisorOutput, supervisor_schema
from lease_renewal.agents.specialists import run_specialists
from lease_renewal.critic.keywords import review
from lease_renewal.decision.policy import (
    Policy,
    action_for,
    arbitrate,
    band_of,
    clamp,
    direction_of,
    has_conflict,
)


def prompt(as_of: str) -> str:
    text = resources.files("lease_renewal.prompts").joinpath("supervisor.md").read_text()
    return text.format(as_of=as_of)


def brief(home: dict, specialists: dict[str, dict], arbitration: dict) -> str:
    """What the supervisor sees: specialist findings plus the code's arbitration outcome."""
    return json.dumps(
        {
            "home_id": home["home_id"],
            "current_rent": home["current_rent"],
            "specialists": {
                name: {
                    "signal": out["signal"],
                    "flags": out["flags"],
                    "finding": out["finding"],
                }
                for name, out in specialists.items()
            },
            "arbitration": arbitration,
        },
        indent=2,
    )


async def run_home_async(home: dict, policy: Policy, as_of: str) -> dict:
    """One multi-agent case: specialists in parallel, code arbitration, supervisor, critic."""
    specialists = await run_specialists(home, as_of)
    signals = {name: out["signal"] for name, out in specialists.items()}
    flags = sorted({f for out in specialists.values() for f in out["flags"]})

    conflict = has_conflict(signals)
    winner, arbitrated_direction = arbitrate(policy, signals)
    arbitration = {
        "conflict": conflict,
        "binding": conflict,
        "winner": winner if conflict else None,
        "direction": arbitrated_direction if conflict else "not constrained",
        "precedence": policy.arbitration_precedence,
    }

    async with httpx.AsyncClient() as client:
        call = await call_json_async(
            client, prompt(as_of), brief(home, specialists, arbitration), supervisor_schema()
        )
    output = SupervisorOutput.model_validate_json(call.content)

    proposed = output.proposed_rent_change_pct
    direction_honoured = (not conflict) or direction_of(proposed) == arbitrated_direction
    clamped = clamp(policy, proposed)
    verdict = review(output.reasoning, output.draft_message, output.arbitration_note)

    spec_tokens_in = sum(o["prompt_tokens"] for o in specialists.values())
    spec_tokens_out = sum(o["completion_tokens"] for o in specialists.values())
    return {
        "home_id": home["home_id"],
        "signals": signals,
        "arbitration": arbitration,
        "direction_honoured": direction_honoured,
        # The supervisor proposes no action. Code resolves it from severity tags
        # (ADR-015), so there is no model action to score in this flow.
        "proposed_action": None,
        "enforced_action": action_for(policy, flags),
        "proposed_rent_change_pct": proposed,
        "clamped_rent_change_pct": clamped,
        "pre_clamp_band": band_of(policy, proposed),
        "band": band_of(policy, clamped),
        "direction": direction_of(clamped),
        "flags": flags,
        "out_of_domain_flags": sorted(
            {f for o in specialists.values() for f in o["out_of_domain_flags"]}
        ),
        "flag_evidence": {k: v for o in specialists.values() for k, v in o["evidence"].items()},
        "specialist_findings": {name: o["finding"] for name, o in specialists.items()},
        "arbitration_note": output.arbitration_note,
        "reasoning": output.reasoning,
        "draft_message": output.draft_message,
        "critic": verdict,
        "state": verdict["verdict"],
        "model": call.model,
        "provider": call.provider,
        "prompt_tokens": spec_tokens_in + call.prompt_tokens,
        "completion_tokens": spec_tokens_out + call.completion_tokens,
        "calls": 4,
    }


def run_all(homes_path, policy: Policy) -> dict:
    """Run every spike home through the multi-agent flow."""
    data = json.loads(homes_path.read_text())
    as_of = data["as_of"]

    async def go():
        return [await run_home_async(home, policy, as_of) for home in data["homes"]]

    return {"as_of": as_of, "runs": asyncio.run(go())}
