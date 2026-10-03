"""Re-grade a recorded run against the current keys. No model calls."""

import json
import sys
from pathlib import Path

from lease_renewal.eval.grade import grade_case, summarise, trap_pair_result

KEYS = Path("data/spike_keys/keys.json")


def main(run_path: str) -> None:
    run = json.loads(Path(run_path).read_text())
    keys = {k["home_id"]: k for k in json.loads(KEYS.read_text())["keys"]}
    runs = {r["home_id"]: r for r in run["runs"]}
    graded = [grade_case(runs[h], keys[h]) for h in runs]
    print(f"{'home':32} {'dir':20} {'band':10} {'exact':6} {'w1':4} action")
    for g in graded:
        dirs = "/".join(g["acceptable_directions"])
        print(
            f"{g['home_id']:32} {g['direction_actual']}->{dirs:14} "
            f"{str(g['band']):10} {str(g['band_exact']):6} "
            f"{str(g['band_within_one']):5} {g['action_pass']}"
        )
    print()
    for name, value in summarise(graded).items():
        print(f"  {name}: {value}")
    print(f"  trap pair match: {trap_pair_result(graded, runs, keys)['outcomes_match']}")


if __name__ == "__main__":
    main(sys.argv[1])
