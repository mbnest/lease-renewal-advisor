"""Single-agent baseline: one model call per home over the full context.

The model proposes an action, a rent change, and flags. Code then enforces the
clamp, the band lookup, and the action implied by the flags' severity tags
(ADR-003, ADR-015, ADR-020). Both the proposal and the enforced result are kept,
so grading can tell a rescued output from a correct one.
"""

import json
from importlib import resources
from pathlib import Path

from lease_renewal.agents.gateway import call_json
from lease_renewal.agents.schema import BaselineOutput, json_schema
from lease_renewal.decision.policy import (
    Policy,
    action_for,
    band_of,
    clamp,
    direction_of,
)


def load_prompt(as_of: str) -> str:
    """Read the baseline system prompt and fill in the run date."""
    text = resources.files("lease_renewal.prompts").joinpath("baseline.md").read_text()
    return text.format(as_of=as_of)


def home_context(home: dict) -> str:
    """The full home record as the model sees it. Answer keys are never included."""
    return json.dumps(home, indent=2)


def run_home(home: dict, policy: Policy, as_of: str) -> dict:
    """Call the model for one home and apply the code-enforced rules to its proposal."""
    call = call_json(load_prompt(as_of), home_context(home), json_schema())
    output = BaselineOutput.model_validate_json(call.content)

    flags = sorted({claim.flag for claim in output.flags})
    clamped = clamp(policy, output.proposed_rent_change_pct)
    return {
        "home_id": home["home_id"],
        "proposed_action": output.proposed_action,
        "enforced_action": action_for(policy, flags),
        "proposed_rent_change_pct": output.proposed_rent_change_pct,
        "clamped_rent_change_pct": clamped,
        "pre_clamp_band": band_of(policy, output.proposed_rent_change_pct),
        "band": band_of(policy, clamped),
        "direction": direction_of(clamped),
        "flags": flags,
        "flag_evidence": {claim.flag: claim.evidence for claim in output.flags},
        "reasoning": output.reasoning,
        "draft_message": output.draft_message,
        "model": call.model,
        "provider": call.provider,
        "prompt_tokens": call.prompt_tokens,
        "completion_tokens": call.completion_tokens,
    }


def run_all(homes_path: Path, policy: Policy) -> dict:
    """Run every home in the spike data file."""
    data = json.loads(homes_path.read_text())
    as_of = data["as_of"]
    return {
        "as_of": as_of,
        "runs": [run_home(home, policy, as_of) for home in data["homes"]],
    }
