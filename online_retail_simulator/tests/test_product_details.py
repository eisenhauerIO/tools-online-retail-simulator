"""Tests for product details simulation."""

import pandas as pd
import pytest

from conftest import OLLAMA_AVAILABLE
from online_retail_simulator.simulate.product_details_mock import simulate_product_details_mock


@pytest.fixture
def sample_products():
    """Sample products DataFrame for testing."""
    return pd.DataFrame(
        [
            {"product_identifier": "A001", "category": "Electronics", "price": 99.99},
            {"product_identifier": "A002", "category": "Clothing", "price": 29.99},
            {"product_identifier": "A003", "category": "Home & Kitchen", "price": 49.99},
        ]
    )


class TestProductDetailsMock:
    """Tests for mock backend."""

    def test_returns_plain_python_strings(self, sample_products):
        """Brand and features are str, so they display without np.str_ wrappers."""
        result = simulate_product_details_mock(sample_products, seed=42)
        for _, row in result.iterrows():
            assert type(row["brand"]) is str
            assert all(type(feature) is str for feature in row["features"])

    def test_adds_required_columns(self, sample_products):
        """Mock should add title, description, brand, features."""
        result = simulate_product_details_mock(sample_products)
        assert "title" in result.columns
        assert "description" in result.columns
        assert "brand" in result.columns
        assert "features" in result.columns

    def test_preserves_original_columns(self, sample_products):
        """Mock should preserve original columns."""
        result = simulate_product_details_mock(sample_products)
        assert "product_identifier" in result.columns
        assert "category" in result.columns
        assert "price" in result.columns

    def test_preserves_row_count(self, sample_products):
        """Mock should return same number of rows."""
        result = simulate_product_details_mock(sample_products)
        assert len(result) == len(sample_products)

    def test_seed_reproducibility(self, sample_products):
        """Same seed should produce same results."""
        result1 = simulate_product_details_mock(sample_products, seed=42)
        result2 = simulate_product_details_mock(sample_products, seed=42)
        pd.testing.assert_frame_equal(result1, result2)

    def test_different_seeds_differ(self, sample_products):
        """Different seeds should produce different results."""
        result1 = simulate_product_details_mock(sample_products, seed=42)
        result2 = simulate_product_details_mock(sample_products, seed=123)
        assert not result1["title"].equals(result2["title"])

    def test_features_is_list(self, sample_products):
        """Features should be a list."""
        result = simulate_product_details_mock(sample_products)
        assert isinstance(result["features"].iloc[0], list)


@pytest.mark.llm
@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama server not available")
class TestProductDetailsOllama:
    """Tests for Ollama backend (requires Ollama server running)."""

    def test_ollama_generates_details(self, sample_products):
        """Ollama should generate product details."""
        from online_retail_simulator.simulate.product_details_ollama import simulate_product_details_ollama

        result = simulate_product_details_ollama(sample_products)

        assert "title" in result.columns
        assert "description" in result.columns
        assert "brand" in result.columns
        assert "features" in result.columns
        assert len(result) == len(sample_products)


def test_simulate_product_details_reproducible_with_seed(tmp_path):
    """A seeded config produces identical product details across runs."""
    from online_retail_simulator import load_job_results, simulate

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
STORAGE:
  PATH: {tmp_path}/output
RULE:
  PRODUCTS:
    FUNCTION: simulate_products_rule_based
    PARAMS:
      num_products: 20
      seed: 7
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-11-01"
      date_end: "2024-11-03"
      seed: 7
PRODUCT_DETAILS:
  FUNCTION: simulate_product_details_mock
"""
    )

    first = load_job_results(simulate(str(config_path)))
    second = load_job_results(simulate(str(config_path)))

    pd.testing.assert_frame_equal(first["products"], second["products"])
    pd.testing.assert_frame_equal(first["metrics"], second["metrics"])


class TestOllamaResponseParsing:
    """Tests for Ollama response handling (no server needed)."""

    PRODUCT = {"product_identifier": "A001", "title": "T", "description": "D", "brand": "B", "features": ["f"]}

    @pytest.mark.parametrize(
        "payload",
        [
            [PRODUCT],
            {"products": [PRODUCT]},
            PRODUCT,
        ],
    )
    def test_parse_batch_accepts_common_shapes(self, payload):
        """A bare list, a wrapped list, and a single object all parse to a list."""
        import json

        from online_retail_simulator.simulate.product_details_ollama import _parse_batch

        assert _parse_batch(json.dumps(payload)) == [self.PRODUCT]

    def test_parse_batch_rejects_unknown_shape(self):
        """An object without a product list or product fields raises ValueError."""
        from online_retail_simulator.simulate.product_details_ollama import _parse_batch

        with pytest.raises(ValueError):
            _parse_batch('{"status": "ok"}')

    def test_retries_until_response_parses(self, monkeypatch):
        """A non-JSON response is retried instead of crashing the batch."""
        import json

        from online_retail_simulator.simulate import product_details_ollama as module

        responses = iter(["Sure! Here is your JSON:", json.dumps({"products": [self.PRODUCT]})])

        class FakeResponse:
            def __init__(self, text):
                self.text = text

            def raise_for_status(self):
                pass

            def json(self):
                return {"response": self.text}

        monkeypatch.setattr(module.requests, "post", lambda *args, **kwargs: FakeResponse(next(responses)))

        assert module._generate_batch("prompt", "model", "url") == [self.PRODUCT]

    def test_raises_after_max_attempts(self, monkeypatch):
        """Persistent garbage raises after MAX_ATTEMPTS requests."""
        from online_retail_simulator.simulate import product_details_ollama as module

        calls = []

        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {"response": "not json"}

        def fake_post(*args, **kwargs):
            calls.append(kwargs["json"])
            return FakeResponse()

        monkeypatch.setattr(module.requests, "post", fake_post)

        with pytest.raises(ValueError):
            module._generate_batch("prompt", "model", "url")
        assert len(calls) == module.MAX_ATTEMPTS
        assert calls[0]["format"] == "json"
