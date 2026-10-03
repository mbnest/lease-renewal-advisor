"""Smoke test that the package imports and the toolchain runs."""

import pytest

import lease_renewal


@pytest.mark.unit
def test_package_imports():
    assert lease_renewal.__doc__
