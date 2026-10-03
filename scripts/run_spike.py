"""Run the single-agent baseline over the spike homes and grade it.

Writes the run and the grading to data/spike_runs/. Live model calls, so this is
never part of CI.
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from lease_renewal.agents.baseline import run_all
from lease_renewal.decision.policy import load_policy
from lease_renewal.eval.grade import grade_case, summarise, trap_pair_result

HOMES = Path("data/spike/homes.json")
KEYS = Path("data/spike_keys/keys.json")
POLICY = Path("config/policy_spike.yaml")
OUT_DIR = Path("data/spike_runs")


def main() -> None:
    policy = load_policy(POLICY)
    result = run_all(HOMES, policy)
    keys = {k["home_id"]: k for k in json.loads(KEYS.read_text())["keys"]}
    runs = {r["home_id"]: r for r in result["runs"]}

    graded = [grade_case(runs[home_id], keys[home_id]) for home_id in runs]
    report = {
        "run_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "policy_version": policy.version,
        "model": result["runs"][0]["model"],
        "provider": result["runs"][0]["provider"],
        "summary": summarise(graded),
        "trap_pair": trap_pair_result(graded, runs, keys),
        "cases": graded,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = report["run_at"].replace(":", "").replace("-", "")
    (OUT_DIR / f"run-{stamp}.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT_DIR / f"grade-{stamp}.json").write_text(json.dumps(report, indent=2) + "\n")

    print(f"model {report['model']} via {report['provider']}  policy {report['policy_version']}")
    print(f"{'home':32} {'action':26} {'dir':16} {'band':10} flags")
    for g in graded:
        action = f"{g['action_enforced']}/{g['action_expected']}"
        direction = f"{g['direction_actual']}/{g['direction_expected']}"
        passed = g["action_pass"] and g["direction_pass"] and g["band_within_one"]
        mark = "ok " if passed else "FAIL"
        print(
            f"{mark} {g['home_id']:28} {action:26} {direction:16} "
            f"{str(g['band']):10} {g['flags_found']}"
        )
    print()
    for name, value in report["summary"].items():
        print(f"  {name}: {value}")
    print(f"  trap pair: {report['trap_pair']}")
    print(f"\nwrote {OUT_DIR}/grade-{stamp}.json")


if __name__ == "__main__":
    sys.exit(main())
