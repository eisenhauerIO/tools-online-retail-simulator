import pandas as pd

from online_retail_simulator.simulate import simulate_characteristics, simulate_metrics


def test_metrics_rule():
    import os

    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    products = simulate_characteristics(config_path)
    df = simulate_metrics(products, config_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "asin" in df.columns
    assert "date" in df.columns
    assert "quantity" in df.columns
    assert "revenue" in df.columns


def test_metrics_rule_weekly_granularity():
    """Test weekly aggregation produces correct output."""
    import os

    config_path = os.path.join(os.path.dirname(__file__), "config_rule_weekly.yaml")
    products = simulate_characteristics(config_path)
    df = simulate_metrics(products, config_path)

    # Basic validations
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "asin" in df.columns
    assert "date" in df.columns
    assert "quantity" in df.columns
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
    product_week_combinations = df.groupby(["asin", "date"]).size()
    assert len(product_week_combinations) == expected_rows, "All product-week combinations should exist"


def test_metrics_rule_weekly_date_adjustment():
    """Test that weekly granularity adjusts dates to full week boundaries."""
    import os

    # The config has date_start: "2024-01-01" (Monday) to date_end: "2024-01-31" (Wednesday)
    # Should expand to 2024-01-01 (Monday) to 2024-02-04 (Sunday) = 5 weeks

    config_path = os.path.join(os.path.dirname(__file__), "config_rule_weekly.yaml")
    products = simulate_characteristics(config_path)
    df = simulate_metrics(products, config_path)

    df["date_dt"] = pd.to_datetime(df["date"])

    # Check first date is Monday
    first_date = df["date_dt"].min()
    assert first_date.weekday() == 0, "First date should be Monday"

    # Jan 1 2024 is Monday, Jan 31 is Wednesday
    # Expanded to Jan 1 (Mon) to Feb 4 (Sun) = 5 weeks
    assert df["date"].nunique() == 5, "Should have 5 weeks from 2024-01-01 to 2024-02-04"
