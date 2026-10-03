"""The committed JSON Schemas must match the Pydantic contracts that generate them."""

from pathlib import Path

import pytest

from lease_renewal.contracts.registry import CONTRACTS, schema_for

SCHEMAS = Path("schemas")


@pytest.mark.validator
@pytest.mark.parametrize("name", sorted(CONTRACTS))
def test_committed_schema_matches_the_model(name):
    """Regenerate with: uv run python scripts/build_schemas.py"""
    path = SCHEMAS / f"{name}.schema.json"
    assert path.exists(), f"{path} is missing. Run scripts/build_schemas.py"
    assert path.read_text() == schema_for(CONTRACTS[name]), (
        f"{path} is stale. Run scripts/build_schemas.py"
    )


@pytest.mark.validator
def test_every_committed_schema_has_a_contract():
    """A schema file with no model behind it would have no source of truth."""
    committed = {p.name.removesuffix(".schema.json") for p in SCHEMAS.glob("*.schema.json")}
    assert committed == set(CONTRACTS)
