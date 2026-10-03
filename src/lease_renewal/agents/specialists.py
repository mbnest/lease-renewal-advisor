"""Run the three specialists in parallel, each on its own data domain."""

import asyncio
import json
from importlib import resources

import httpx

from lease_renewal.agents.domains import DOMAIN_FLAGS, slice_for
from lease_renewal.agents.gateway import call_json_async
from lease_renewal.agents.multi_schema import SpecialistOutput, specialist_schema

SPECIALISTS = ("condition", "market", "resident")

FLAG_RULES = {
    "chronic_maintenance": (
        "- chronic_maintenance: 3 or more work orders on the SAME system within "
        "12 months, or maintenance cost above 5 percent of annual rent"
    ),
    "below_market": "- below_market: current rent at least 8 percent below the comp median",
    "soft_demand": "- soft_demand: city demand is soft AND the comp trend is flat or down",
    "late_payment_pattern": "- late_payment_pattern: 3 or more late payments within 12 months",
    "open_complaint": (
        "- open_complaint: a complaint still unresolved 30 or more days after it was opened"
    ),
}

SIGNAL_RULES = {
    "condition": (
        "- ESCALATE when you raise a flag that needs a non-rent human action\n"
        "- NONE when you raise no flag. Never return RAISE or HOLD."
    ),
    "market": (
        "- RAISE when the market supports a higher rent\n"
        "- HOLD when the market does not support an increase\n"
        "- NONE when the market data shows nothing notable. Never return ESCALATE."
    ),
    "resident": (
        "- RAISE when the resident history supports a higher rent\n"
        "- HOLD when the resident history argues against an increase\n"
        "- NONE when the resident data shows nothing notable. Never return ESCALATE."
    ),
}


def prompt_for(specialist: str, as_of: str) -> str:
    """Build one specialist's system prompt from its own flag and signal rules."""
    text = resources.files("lease_renewal.prompts").joinpath("specialist.md").read_text()
    rules = "\n".join(FLAG_RULES[f] for f in DOMAIN_FLAGS[specialist])
    return text.format(
        specialist=specialist, flag_rules=rules, signal_rules=SIGNAL_RULES[specialist], as_of=as_of
    )


async def run_specialists(home: dict, as_of: str) -> dict[str, dict]:
    """Call all three specialists concurrently and return their validated outputs."""
    schema = specialist_schema()

    async def one(client: httpx.AsyncClient, name: str) -> tuple[str, dict]:
        call = await call_json_async(
            client, prompt_for(name, as_of), json.dumps(slice_for(home, name), indent=2), schema
        )
        output = SpecialistOutput.model_validate_json(call.content)
        allowed = set(DOMAIN_FLAGS[name])
        return name, {
            "signal": output.signal,
            "flags": sorted({c.flag for c in output.flags if c.flag in allowed}),
            "out_of_domain_flags": sorted({c.flag for c in output.flags if c.flag not in allowed}),
            "evidence": {c.flag: c.evidence for c in output.flags},
            "finding": output.finding,
            "prompt_tokens": call.prompt_tokens,
            "completion_tokens": call.completion_tokens,
        }

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(one(client, name) for name in SPECIALISTS))
    return dict(results)
