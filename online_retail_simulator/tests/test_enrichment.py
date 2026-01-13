"""Tests for enrichment functionality."""

import os
import tempfile

import pandas as pd
import pytest

from online_retail_simulator import enrich, simulate


def test_enrich_basic():
    """Test basic enrichment functionality."""
    # Create test config
    config_content = """
IMPACT:
  FUNCTION: "quantity_boost"
  PARAMS:
    effect_size: 0.5
    enrichment_fraction: 0.5
    enrichment_start: "2024-01-02"
    seed: 42
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info = simulate(test_config_path)

        # Load original sales before enrichment
        original_metrics = job_info.load_df("metrics")

        # Apply enrichment
        enriched_job_info = enrich(config_path, job_info)

        # Load enriched data
        enriched_metrics = enriched_job_info.load_df("enriched")

        # Verify structure
        assert isinstance(enriched_metrics, pd.DataFrame)
        assert len(enriched_metrics) == len(original_metrics)
        # All original columns should be present, plus the new 'enriched' column
        assert all(col in enriched_metrics.columns for col in original_metrics.columns)
        assert "enriched" in enriched_metrics.columns

        # Verify enriched column has proper boolean values
        assert enriched_metrics["enriched"].dtype == bool
        # With 50% enrichment_fraction, we expect roughly half of unique products to be enriched
        enriched_products = enriched_metrics[enriched_metrics["enriched"]]["product_identifier"].nunique()
        total_products = enriched_metrics["product_identifier"].nunique()
        assert 0.3 <= enriched_products / total_products <= 0.7  # Allow some variance

        # Verify enrichment effect (should have some ordered units increases)
        post_enrichment = enriched_metrics[enriched_metrics["date"] >= "2024-01-02"]
        original_post = original_metrics[original_metrics["date"] >= "2024-01-02"]

        # Total ordered units should increase due to enrichment
        assert post_enrichment["ordered_units"].sum() >= original_post["ordered_units"].sum()

    finally:
        os.unlink(config_path)


def test_enrich_product_detail_boost():
    """Test product detail boost with ramp-up."""
    config_content = """
IMPACT:
  FUNCTION: "product_detail_boost"
  PARAMS:
    effect_size: 0.3
    ramp_days: 3
    enrichment_fraction: 0.4
    enrichment_start: "2024-01-03"
    seed: 123
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info = simulate(test_config_path)

        # Load original sales before enrichment
        original_metrics = job_info.load_df("metrics")

        # Apply enrichment
        enriched_job_info = enrich(config_path, job_info)

        # Load enriched data
        enriched_metrics = enriched_job_info.load_df("enriched")

        # Verify basic structure
        assert isinstance(enriched_metrics, pd.DataFrame)
        assert len(enriched_metrics) == len(original_metrics)

        # Verify enrichment effect exists
        post_enrichment = enriched_metrics[enriched_metrics["date"] >= "2024-01-03"]
        original_post = original_metrics[original_metrics["date"] >= "2024-01-03"]

        assert post_enrichment["ordered_units"].sum() >= original_post["ordered_units"].sum()

    finally:
        os.unlink(config_path)


def test_enrich_invalid_config():
    """Test error handling for invalid config."""
    config_content = """
INVALID_KEY: "test"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info = simulate(test_config_path)

        # Should raise error for missing IMPACT
        with pytest.raises(ValueError, match="Config must include 'IMPACT' specification"):
            enrich(config_path, job_info)

    finally:
        os.unlink(config_path)


def test_enrich_invalid_dataframe():
    """Test error handling for invalid DataFrame."""
    config_content = """
IMPACT:
  FUNCTION: "quantity_boost"
  PARAMS:
    effect_size: 0.5
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Test with invalid job_info
        from online_retail_simulator import JobInfo

        invalid_job_info = JobInfo("invalid-job-id", ".")
        with pytest.raises(FileNotFoundError, match="metrics.csv not found"):
            enrich(config_path, invalid_job_info)

    finally:
        os.unlink(config_path)


def test_enrich_reproducibility():
    """Test that enrichment effect is reproducible with same seed."""
    config_content = """
IMPACT:
  FUNCTION: "quantity_boost"
  PARAMS:
    effect_size: 0.2
    enrichment_fraction: 0.3
    enrichment_start: "2024-01-02"
    seed: 999
    min_units: 0
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate same test data twice (with fixed seed in config)
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info1 = simulate(test_config_path)
        job_info2 = simulate(test_config_path)

        # Load original sales
        metrics1 = job_info1.load_df("metrics")
        metrics2 = job_info2.load_df("metrics")

        # Apply enrichment with same config (same seed)
        enriched_job_info1 = enrich(config_path, job_info1)
        enriched_job_info2 = enrich(config_path, job_info2)

        # Load enriched results
        enriched_df1 = enriched_job_info1.load_df("enriched")
        enriched_df2 = enriched_job_info2.load_df("enriched")

        # Both should have identical structure
        assert list(enriched_df1.columns) == list(enriched_df2.columns)
        assert len(enriched_df1) == len(enriched_df2)

        # Enrichment effect (ratio of enriched/original) should be the same
        # since both use the same seed for enrichment
        effect1 = enriched_df1["ordered_units"].sum() / metrics1["ordered_units"].sum()
        effect2 = enriched_df2["ordered_units"].sum() / metrics2["ordered_units"].sum()
        assert abs(effect1 - effect2) < 0.01, "Enrichment effect should be reproducible"

    finally:
        os.unlink(config_path)
