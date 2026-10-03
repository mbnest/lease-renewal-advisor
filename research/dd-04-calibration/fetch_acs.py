"""Fetch ACS 5-year median gross rent for the seven DFW cities.

Reads CENSUS_API_KEY from the environment. Writes acs_places_2024.csv.
Run: uv run --no-project --env-file .env research/dd-04-calibration/fetch_acs.py
"""

import csv
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

YEAR = 2024
CITIES = {
    "Dallas city, Texas": "Dallas",
    "Fort Worth city, Texas": "Fort Worth",
    "Arlington city, Texas": "Arlington",
    "Plano city, Texas": "Plano",
    "Lewisville city, Texas": "Lewisville",
    "Prosper town, Texas": "Prosper",
    "Highland Park town, Texas": "Highland Park",
}
VARIABLES = {
    "B25064_001E": "median_gross_rent",
    "B25031_004E": "median_gross_rent_2br",
    "B25031_005E": "median_gross_rent_3br",
}
OUT = Path(__file__).parent / f"acs_places_{YEAR}.csv"


def fetch_places() -> list[list[str]]:
    """Return ACS rows for every Texas place."""
    query = urlencode({
        "get": ",".join(["NAME", *VARIABLES]),
        "for": "place:*",
        "in": "state:48",
        "key": os.environ["CENSUS_API_KEY"],
    })
    with urlopen(f"https://api.census.gov/data/{YEAR}/acs/acs5?{query}") as resp:
        return json.load(resp)


def main() -> None:
    """Keep the seven cities and write them to CSV."""
    header, *rows = fetch_places()
    picked = [dict(zip(header, r)) for r in rows if r[0] in CITIES]
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["city", "place_fips", *VARIABLES.values()])
        for r in sorted(picked, key=lambda r: CITIES[r["NAME"]]):
            w.writerow([CITIES[r["NAME"]], r["place"], *(r[v] for v in VARIABLES)])
    print(f"wrote {len(picked)} of {len(CITIES)} cities to {OUT.name}")


if __name__ == "__main__":
    main()
