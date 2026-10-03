"""Summarize HUD SAFMR and Census ACS rents per city for DD-04.

Reads city_zips.csv, safmr_city_zips.csv, acs_places_2024.csv. Prints a markdown table.
Run: uv run --no-project research/dd-04-calibration/summarize.py
"""

import csv
from collections import defaultdict
from pathlib import Path
from statistics import median

HERE = Path(__file__).parent
ORDER = ["Highland Park", "Prosper", "Plano", "Lewisville", "Dallas", "Fort Worth", "Arlington"]


def read(name: str) -> list[dict]:
    """Read a CSV in this folder as dict rows."""
    with (HERE / name).open() as f:
        return list(csv.DictReader(f))


def pct(old: int, new: int) -> float:
    """Percent change from old to new."""
    return 100 * (new - old) / old


def safmr_by_city() -> dict[str, list[dict]]:
    """Group SAFMR ZIP rows by city."""
    city_of = {r["zip"]: r["city"] for r in read("city_zips.csv")}
    out = defaultdict(list)
    for r in read("safmr_city_zips.csv"):
        out[city_of[r["zip"]]].append({k: v if k in ("zip", "hud_area_code") else int(v) for k, v in r.items()})
    return out


def city_row(city: str, rows: list[dict], acs: dict) -> str:
    """Format one city's summary as a markdown table row."""
    rent3 = [r["fy2027_3br"] for r in rows]
    yoy = [pct(r["fy2026_3br"], r["fy2027_3br"]) for r in rows]
    acs3 = acs["median_gross_rent_3br"]
    acs3 = "suppressed" if acs3.startswith("-") else acs3
    return (f"| {city} | {acs['median_gross_rent']} | {acs3} | {len(rows)} | {median(rent3):.0f} "
            f"| {min(rent3)} to {max(rent3)} | {median(yoy):+.1f} | {min(yoy):+.1f} to {max(yoy):+.1f} |")


def main() -> None:
    """Print the per-city table and the pooled year-over-year spread."""
    acs = {r["city"]: r for r in read("acs_places_2024.csv")}
    by_city = safmr_by_city()
    print("| City | ACS median gross rent | ACS 3BR | ZIPs | SAFMR FY2027 3BR median | 3BR range "
          "| 3BR FY26 to FY27 median % | 3BR FY26 to FY27 range % |")
    print("|---|---|---|---|---|---|---|---|")
    for city in ORDER:
        print(city_row(city, by_city[city], acs[city]))
    allyoy = sorted(pct(r["fy2026_3br"], r["fy2027_3br"]) for rows in by_city.values() for r in rows)
    print(f"\nPooled 3BR FY26 to FY27 across {len(allyoy)} ZIPs: median {median(allyoy):+.1f}%, "
          f"min {allyoy[0]:+.1f}%, max {allyoy[-1]:+.1f}%")


if __name__ == "__main__":
    main()
