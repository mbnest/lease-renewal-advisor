"""Run the multi-agent flow over the spike homes and compare it to the baseline.

Live model calls, four per home. Never part of CI.
"""

import glob
import json
from datetime import UTC, datetime
from pathlib import Path

from lease_renewal.agents import supervisor
from lease_renewal.decision.policy import load_policy
from lease_renewal.eval.grade import grade_case, summarise, trap_pair_result

HOMES = Path("data/spike/homes.json")
KEYS = Path("data/spike_keys/keys.json")
POLICY = Path("config/policy_spike.yaml")
OUT_DIR = Path("data/spike_runs")


def latest_baseline() -> dict | None:
    """The most recent step 1 run, for the per-home comparison."""
    runs = sorted(glob.glob(str(OUT_DIR / "run-*.json")))
    return json.loads(Path(runs[-1]).read_text()) if runs else None


def main() -> None:
    policy = load_policy(POLICY)
    keys = {k["home_id"]: k for k in json.loads(KEYS.read_text())["keys"]}
    result = supervisor.run_all(HOMES, policy)
    runs = {r["home_id"]: r for r in result["runs"]}
    graded = [grade_case(runs[h], keys[h]) for h in runs]

    base = latest_baseline()
    base_runs = {r["home_id"]: r for r in base["runs"]} if base else {}
    base_graded = {g["home_id"]: g for g in (grade_case(base_runs[h], keys[h]) for h in base_runs)}

    report = {
        "run_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "flow": "multi_agent",
        "policy_version": policy.version,
        "model": result["runs"][0]["model"],
        "summary": summarise(graded),
        "trap_pair": trap_pair_result(graded, runs, keys),
        "cases": graded,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = report["run_at"].replace(":", "").replace("-", "")
    (OUT_DIR / f"multi-{stamp}.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT_DIR / f"multi-grade-{stamp}.json").write_text(json.dumps(report, indent=2) + "\n")

    print(f"multi-agent vs baseline, model {report['model']}, policy {policy.version}\n")
    header = f"{'home':30} {'band multi':11} {'band base':11} {'state':9} arb"
    print(header)
    for g in graded:
        run = runs[g["home_id"]]
        b = base_graded.get(g["home_id"], {})
        arb = run["arbitration"]
        tag = f"{arb['winner']}->{arb['direction']}" if arb["binding"] else "not bound"
        multi = f"{g['band']}{'*' if g['band_exact'] else ''}"
        base_band = f"{b.get('band')}{'*' if b.get('band_exact') else ''}"
        print(f"{g['home_id']:30} {multi:11} {base_band:11} {run['state']:9} {tag}")
    print("\n* band exact\n")
    base_sum = summarise(list(base_graded.values())) if base_graded else {}
    for name, value in report["summary"].items():
        before = base_sum.get(name)
        print(f"  {name}: {value}   (baseline {before})")
    print(f"  trap pair: {report['trap_pair']}")
    print(
        f"  direction honoured: {sum(r['direction_honoured'] for r in runs.values())}/{len(runs)}"
    )
    print(f"  out of domain flags: {[r['out_of_domain_flags'] for r in runs.values()]}")
    print(f"\nwrote {OUT_DIR}/multi-grade-{stamp}.json")


if __name__ == "__main__":
    main()
