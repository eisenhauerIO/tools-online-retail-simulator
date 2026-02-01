"""Tests for the backend plugin architecture."""

import pandas as pd
import pytest

from online_retail_simulator.core.backends import (
    BackendRegistry,
    RuleBackend,
    SimulationBackend,
    SynthesizerBackend,
)


class TestBackendRegistry:
    """Tests for BackendRegistry."""

    def test_detect_rule_backend(self):
        """Detects RULE backend from config."""
        config = {"RULE": {"PRODUCTS": {}, "METRICS": {}}}
        backend = BackendRegistry.detect_backend(config)
        assert isinstance(backend, RuleBackend)

    def test_detect_synthesizer_backend(self):
        """Detects SYNTHESIZER backend from config."""
        config = {"SYNTHESIZER": {"PRODUCTS": {}, "METRICS": {}}}
        backend = BackendRegistry.detect_backend(config)
        assert isinstance(backend, SynthesizerBackend)

    def test_missing_backend_raises(self):
        """Raises ValueError when no known backend key in config."""
        config = {"UNKNOWN": {}}
        with pytest.raises(ValueError, match="must contain one of"):
            BackendRegistry.detect_backend(config)

    def test_empty_config_raises(self):
        """Raises ValueError for empty config."""
        with pytest.raises(ValueError):
            BackendRegistry.detect_backend({})


class TestRuleBackend:
    """Tests for RuleBackend."""

    def test_get_key(self):
        """Returns correct config key."""
        assert RuleBackend.get_key() == "RULE"

    def test_simulate_products_returns_dataframe(self, config_products_basic):
        """Products simulation returns DataFrame."""
        backend = RuleBackend(config_products_basic)
        result = backend.simulate_products()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5

    def test_simulate_metrics_returns_dataframe(self, config_metrics_with_rates):
        """Metrics simulation returns DataFrame."""
        products = pd.DataFrame(
            {
                "product_identifier": ["B001", "B002"],
                "category": ["Electronics", "Books"],
                "price": [99.99, 19.99],
            }
        )
        backend = RuleBackend(config_metrics_with_rates)
        result = backend.simulate_metrics(products)
        assert isinstance(result, pd.DataFrame)
        assert "impressions" in result.columns


class TestSynthesizerBackend:
    """Tests for SynthesizerBackend."""

    def test_get_key(self):
        """Returns correct config key."""
        assert SynthesizerBackend.get_key() == "SYNTHESIZER"


class TestBackendRegistration:
    """Tests for backend registration decorator."""

    def test_rule_backend_registered(self):
        """RuleBackend is registered."""
        assert "RULE" in BackendRegistry._backends

    def test_synthesizer_backend_registered(self):
        """SynthesizerBackend is registered."""
        assert "SYNTHESIZER" in BackendRegistry._backends

    def test_simulation_backend_is_abstract(self):
        """SimulationBackend cannot be instantiated directly."""
        with pytest.raises(TypeError):
            SimulationBackend({})
