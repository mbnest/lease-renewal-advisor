"""Write the committed JSON Schemas from the Pydantic contracts.

Run after changing any contract. A test fails when the committed files are stale.
"""

from pathlib import Path

from lease_renewal.contracts.registry import CONTRACTS, schema_for

OUT = Path("schemas")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, model in CONTRACTS.items():
        path = OUT / f"{name}.schema.json"
        path.write_text(schema_for(model))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
