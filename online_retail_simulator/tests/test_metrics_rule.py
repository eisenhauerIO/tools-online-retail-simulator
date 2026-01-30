import os

import pandas as pd

from online_retail_simulator.simulate import simulate_metrics, simulate_products


def test_metrics_rule():
    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    job_info = simulate_products(config_path)
    job_info = simulate_metrics(job_info, config_path)

    df = job_info.load_df("metrics")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "product_identifier" in df.columns
    assert "date" in df.columns
    assert "impressions" in df.columns
    assert "visits" in df.columns
    assert "cart_adds" in df.columns
    assert "ordered_units" in df.columns
    assert "revenue" in df.columns


def test_metrics_rule_weekly_granularity():
    """Test weekly aggregation produces correct output."""
    config_path = os.path.join(os.path.dirname(__file__), "config_rule_weekly.yaml")
    job_info = simulate_products(config_path)
    products = job_info.load_df("products")
    job_info = simulate_metrics(job_info, config_path)
    df = job_info.load_df("metrics")

    # Basic validations
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "product_identifier" in df.columns
    assert "date" in df.columns
    assert "impressions" in df.columns
    assert "visits" in df.columns
    assert "cart_adds" in df.columns
    assert "ordered_units" in df.columns
    assert "revenue" in df.columns

    # Weekly-specific validations
    df["date_dt"] = pd.to_datetime(df["date"])

    # All dates should be Mondays (weekday = 0)
    assert all(df["date_dt"].dt.weekday == 0), "All dates should be Mondays (ISO week start)"

    # Calculate expected dimensions
    unique_products = len(products)
    unique_weeks = df["date"].nunique()

    # Weekly should have fewer rows than if we had generated daily for the same expanded date range
    # With 10 products and 5 weeks (35 days from Jan 1 - Feb 4), we expect:
    # Weekly: 10 products × 5 weeks = 50 rows
    # Daily would be: 10 products × 35 days = 350 rows
    # So weekly has ~7x fewer rows
    expected_weekly_rows = unique_products * unique_weeks
    expected_daily_rows = unique_products * 35  # 5 weeks = 35 days
    assert len(df) == expected_weekly_rows
    assert expected_weekly_rows < expected_daily_rows, "Weekly should have fewer rows than equivalent daily"

    # Verify all products appear in each week (complete grid with no missing rows)
    expected_rows = unique_products * unique_weeks
    assert len(df) == expected_rows, f"Expected {expected_rows} rows (products × weeks), got {len(df)}"

    # Verify data integrity: all combinations of product and week exist
    product_week_combinations = df.groupby(["product_identifier", "date"]).size()
    assert len(product_week_combinations) == expected_rows, "All product-week combinations should exist"


def test_metrics_rule_weekly_date_adjustment():
    """Test that weekly granularity adjusts dates to full week boundaries."""
    # The config has date_start: "2024-01-01" (Monday) to date_end: "2024-01-31" (Wednesday)
    # Should expand to 2024-01-01 (Monday) to 2024-02-04 (Sunday) = 5 weeks

    config_path = os.path.join(os.path.dirname(__file__), "config_rule_weekly.yaml")
    job_info = simulate_products(config_path)
    job_info = simulate_metrics(job_info, config_path)
    df = job_info.load_df("metrics")

    df["date_dt"] = pd.to_datetime(df["date"])

    # Check first date is Monday
    first_date = df["date_dt"].min()
    assert first_date.weekday() == 0, "First date should be Monday"

    # Jan 1 2024 is Monday, Jan 31 is Wednesday
    # Expanded to Jan 1 (Mon) to Feb 4 (Sun) = 5 weeks
    assert df["date"].nunique() == 5, "Should have 5 weeks from 2024-01-01 to 2024-02-04"


def test_funnel_metrics_schema():
    """Test that new funnel metrics are present with correct types."""
    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    job_info = simulate_products(config_path)
    job_info = simulate_metrics(job_info, config_path)
    df = job_info.load_df("metrics")

    # Check all funnel columns exist
    assert "impressions" in df.columns
    assert "visits" in df.columns
    assert "cart_adds" in df.columns
    assert "ordered_units" in df.columns
    assert "revenue" in df.columns

    # Check data types
    assert df["impressions"].dtype == int
    assert df["visits"].dtype == int
    assert df["cart_adds"].dtype == int
    assert df["ordered_units"].dtype == int
    assert df["revenue"].dtype == float


def test_funnel_logic_consistency():
    """Test that funnel stages follow logical hierarchy."""
    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    job_info = simulate_products(config_path)
    job_info = simulate_metrics(job_info, config_path)
    df = job_info.load_df("metrics")

    # Filter to rows with any activity
    active_rows = df[df["impressions"] > 0]

    # Funnel should decrease or stay same at each stage
    assert all(active_rows["visits"] <= active_rows["impressions"])
    assert all(active_rows["cart_adds"] <= active_rows["visits"])
    assert all(active_rows["ordered_units"] <= active_rows["cart_adds"])

    # If ordered_units > 0, revenue should be > 0
    assert all(df[df["ordered_units"] > 0]["revenue"] > 0)

    # If ordered_units = 0, revenue should be 0
    assert all(df[df["ordered_units"] == 0]["revenue"] == 0)


def test_funnel_zero_activity():
    """Test products with zero funnel activity have all zeros."""
    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    job_info = simulate_products(config_path)
    job_info = simulate_metrics(job_info, config_path)
    df = job_info.load_df("metrics")

    # Find rows with no impressions
    no_activity = df[df["impressions"] == 0]

    # All funnel metrics should be zero
    assert all(no_activity["visits"] == 0)
    assert all(no_activity["cart_adds"] == 0)
    assert all(no_activity["ordered_units"] == 0)
    assert all(no_activity["revenue"] == 0.0)


def test_weekly_funnel_aggregation():
    """Test weekly aggregation of funnel metrics."""
    config_path = os.path.join(os.path.dirname(__file__), "config_rule_weekly.yaml")
    job_info = simulate_products(config_path)
    job_info = simulate_metrics(job_info, config_path)
    df = job_info.load_df("metrics")

    # Check schema
    assert "impressions" in df.columns
    assert "visits" in df.columns
    assert "cart_adds" in df.columns
    assert "ordered_units" in df.columns

    # All dates should be Mondays
    df["date_dt"] = pd.to_datetime(df["date"])
    assert all(df["date_dt"].dt.weekday == 0)


def test_conversion_rate_config():
    """Test that custom conversion rates are respected."""
    import tempfile

    import yaml

    # Create custom config with extreme rates for testing
    config = {
        "RULE": {
            "PRODUCTS": {
                "FUNCTION": "simulate_products_rule_based",
                "PARAMS": {"num_products": 5, "seed": 42},
            },
            "METRICS": {
                "FUNCTION": "simulate_metrics_rule_based",
                "PARAMS": {
                    "date_start": "2024-01-01",
                    "date_end": "2024-01-02",
                    "sale_prob": 1.0,  # Always trigger funnel
                    "seed": 42,
                    "granularity": "daily",
                    "impression_to_visit_rate": 1.0,  # 100% conversion
                    "visit_to_cart_rate": 1.0,
                    "cart_to_order_rate": 1.0,
                },
            },
        }
    }

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config, f)
        config_path = f.name

    try:
        job_info = simulate_products(config_path)
        job_info = simulate_metrics(job_info, config_path)
        df = job_info.load_df("metrics")

        # With 100% rates and guaranteed funnel activity:
        # All rows should have activity
        assert all(df["impressions"] > 0)
        assert all(df["visits"] > 0)

        # Most should convert through funnel (allowing for randomness)
        assert (df["cart_adds"] > 0).sum() / len(df) > 0.5

    finally:
        os.unlink(config_path)
