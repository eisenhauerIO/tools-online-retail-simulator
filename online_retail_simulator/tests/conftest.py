"""Shared pytest fixtures for test configuration."""

from pathlib import Path

import pytest
import yaml

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Load a YAML fixture by name."""
    with open(FIXTURES_DIR / name) as f:
        return yaml.safe_load(f)


@pytest.fixture
def config_products_basic():
    """Products simulation config."""
    return load_fixture("config_products_basic.yaml")


@pytest.fixture
def config_metrics_with_rates():
    """Metrics config with conversion rates."""
    return load_fixture("config_metrics_with_rates.yaml")


@pytest.fixture
def config_rule_full():
    """Full RULE backend config."""
    return load_fixture("config_rule_full.yaml")


@pytest.fixture
def config_randomness_test():
    """Base config for randomness tests."""
    return load_fixture("config_randomness_test.yaml")
