"""
Rule-based product metrics simulation (minimal skeleton).
"""

from typing import Dict

import pandas as pd


def simulate_metrics_rule_based(product_characteristics: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    Generate synthetic daily product metrics (rule-based).
    Args:
        product_characteristics: DataFrame of product characteristics
        config: Complete configuration dictionary
    Returns:
        DataFrame of product metrics (one row per product per date, with all characteristics)
    """
    import random
    from datetime import datetime, timedelta

    params = config["RULE"]["METRICS"]["PARAMS"]
    date_start, date_end, sale_prob, seed = (
        params["date_start"],
        params["date_end"],
        params["sale_prob"],
        params["seed"],
    )
    granularity = params["granularity"]

    if seed is not None:
        random.seed(seed)

    start_date = datetime.strptime(date_start, "%Y-%m-%d")
    end_date = datetime.strptime(date_end, "%Y-%m-%d")

    # For weekly granularity, adjust date range to full week boundaries (Monday-Sunday).
    # This ensures we generate complete weeks for clean aggregation.
    # If user requests 2024-01-03 to 2024-01-25, we expand to 2024-01-01 (Monday) to 2024-01-28 (Sunday).
    if granularity == "weekly":
        # Move start_date back to Monday of that week
        start_date = start_date - timedelta(days=start_date.weekday())
        # Move end_date forward to Sunday of that week
        end_date = end_date + timedelta(days=(6 - end_date.weekday()))

    rows = []
    current_date = start_date
    while current_date <= end_date:
        for _, prod in product_characteristics.iterrows():
            sale_occurred = random.random() < sale_prob
            if sale_occurred:
                quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
                revenue = round(prod["price"] * quantity, 2)
            else:
                quantity = 0
                revenue = 0.0
            row = prod.to_dict()
            row["date"] = current_date.strftime("%Y-%m-%d")
            row["quantity"] = quantity
            row["revenue"] = revenue
            rows.append(row)
        current_date += timedelta(days=1)

    daily_df = pd.DataFrame(rows)

    # Aggregate to weekly if requested
    if granularity == "weekly":
        return _aggregate_to_weekly(daily_df, product_characteristics)

    return daily_df


def _aggregate_to_weekly(daily_df: pd.DataFrame, product_characteristics: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate daily metrics to weekly granularity using ISO weeks (Monday-Sunday).

    IMPORTANT: Includes ALL products for ALL weeks, even with zero sales (quantity=0, revenue=0.0).
    This ensures the weekly DataFrame has the same completeness as daily data.

    Args:
        daily_df: Daily metrics DataFrame with columns [asin, category, price, date, quantity, revenue]
        product_characteristics: Original product characteristics DataFrame

    Returns:
        Weekly aggregated DataFrame with same schema, date = week start (Monday)
    """
    # Convert date strings to datetime for week calculation
    df = daily_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Get ISO week start (Monday) for each date
    df["week_start"] = df["date"] - pd.to_timedelta(df["date"].dt.weekday, unit="d")

    # Get unique weeks in the date range
    unique_weeks = df["week_start"].unique()

    # Create complete product × week grid to ensure zero-sale rows are included
    products = product_characteristics[["asin", "category", "price"]].copy()
    week_grid = pd.DataFrame({"week_start": unique_weeks})
    complete_grid = products.merge(week_grid, how="cross")

    # Aggregate actual sales by product and week
    sales_agg = df.groupby(["asin", "category", "price", "week_start"], as_index=False).agg(
        {"quantity": "sum", "revenue": "sum"}
    )

    # Merge with complete grid to fill in zero-sale weeks
    weekly = complete_grid.merge(sales_agg, on=["asin", "category", "price", "week_start"], how="left")

    # Fill NaN values with 0 (weeks with no sales)
    weekly["quantity"] = weekly["quantity"].fillna(0).astype(int)
    weekly["revenue"] = weekly["revenue"].fillna(0.0)

    # Convert week_start back to string format YYYY-MM-DD
    weekly["date"] = weekly["week_start"].dt.strftime("%Y-%m-%d")
    weekly = weekly.drop(columns=["week_start"])

    # Reorder columns to match original schema
    weekly = weekly[["asin", "category", "price", "date", "quantity", "revenue"]]

    return weekly
