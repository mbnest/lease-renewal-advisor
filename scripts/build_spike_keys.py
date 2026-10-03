"""Write the spike answer keys from the homes and the policy config.

Keys land outside the agent-readable data directory (ADR-024). Rerun after any
change to the homes, the policy config, or the recompute rules.
"""

import json
from datetime import date
from pathlib import Path

from lease_renewal.decision.policy import load_policy
from lease_renewal.generator.keys import key_for

HOMES = Path("data/spike/homes.json")
POLICY = Path("config/policy_spike.yaml")
OUT = Path("data/spike_keys/keys.json")


def main() -> None:
    policy = load_policy(POLICY)
    data = json.loads(HOMES.read_text())
    as_of = date.fromisoformat(data["as_of"])
    keys = [key_for(home, policy, as_of) for home in data["homes"]]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"as_of": data["as_of"], "keys": keys}, indent=2) + "\n")
    for key in keys:
        print(
            f"{key['home_id']:32} {key['expected_action']:16} "
            f"{key['expected_direction']:7} {key['acceptable_bands']} "
            f"flags={key['required_flags']}"
        )


if __name__ == "__main__":
    main()
