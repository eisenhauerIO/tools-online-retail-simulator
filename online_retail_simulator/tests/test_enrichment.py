"""Tests for enrichment functionality."""

import os
import tempfile

import pandas as pd
import pytest

from online_retail_simulator import enrich, load_dataframe, simulate


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
        original_sales = load_dataframe(job_info, "sales")

        # Apply enrichment
        enriched_job_info = enrich(config_path, job_info)

        # Load enriched data
        enriched_sales = load_dataframe(enriched_job_info, "enriched")

        # Verify structure
        assert isinstance(enriched_sales, pd.DataFrame)
        assert len(enriched_sales) == len(original_sales)
        assert list(enriched_sales.columns) == list(original_sales.columns)

        # Verify enrichment effect (should have some ordered units increases)
        post_enrichment = enriched_sales[enriched_sales["date"] >= "2024-01-02"]
        original_post = original_sales[original_sales["date"] >= "2024-01-02"]

        # Total ordered units should increase due to enrichment
        assert post_enrichment["ordered_units"].sum() >= original_post["ordered_units"].sum()

    finally:
        os.unlink(config_path)


def test_enrich_combined_boost():
    """Test combined boost with ramp-up."""
    config_content = """
IMPACT:
  FUNCTION: "combined_boost"
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
        original_sales = load_dataframe(job_info, "sales")

        # Apply enrichment
        enriched_job_info = enrich(config_path, job_info)

        # Load enriched data
        enriched_sales = load_dataframe(enriched_job_info, "enriched")

        # Verify basic structure
        assert isinstance(enriched_sales, pd.DataFrame)
        assert len(enriched_sales) == len(original_sales)

        # Verify enrichment effect exists
        post_enrichment = enriched_sales[enriched_sales["date"] >= "2024-01-03"]
        original_post = original_sales[original_sales["date"] >= "2024-01-03"]

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
        with pytest.raises(FileNotFoundError, match="sales.csv not found"):
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
        sales1 = load_dataframe(job_info1, "sales")
        sales2 = load_dataframe(job_info2, "sales")

        # Apply enrichment with same config (same seed)
        enriched_job_info1 = enrich(config_path, job_info1)
        enriched_job_info2 = enrich(config_path, job_info2)

        # Load enriched results
        enriched_df1 = load_dataframe(enriched_job_info1, "enriched")
        enriched_df2 = load_dataframe(enriched_job_info2, "enriched")

        # Both should have identical structure
        assert list(enriched_df1.columns) == list(enriched_df2.columns)
        assert len(enriched_df1) == len(enriched_df2)

        # Enrichment effect (ratio of enriched/original) should be the same
        # since both use the same seed for enrichment
        effect1 = enriched_df1["ordered_units"].sum() / sales1["ordered_units"].sum()
        effect2 = enriched_df2["ordered_units"].sum() / sales2["ordered_units"].sum()
        assert abs(effect1 - effect2) < 0.01, "Enrichment effect should be reproducible"

    finally:
        os.unlink(config_path)
