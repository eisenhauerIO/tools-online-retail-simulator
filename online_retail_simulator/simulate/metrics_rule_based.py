"""
Rule-based product metrics simulation (minimal skeleton).
"""

from typing import Dict

import pandas as pd


def simulate_metrics_rule_based(product_characteristics: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    Generate synthetic product metrics with customer journey funnel (rule-based).

    Simulates a realistic conversion funnel: impressions → visits → cart adds → orders.

    Args:
        product_characteristics: DataFrame of product characteristics
        config: Complete configuration dictionary
    Returns:
        DataFrame of product metrics (one row per product per time period).
        Columns: asin, category, price, date, impressions, visits, cart_adds,
        ordered_units, revenue, average_selling_price.
    """
    import random
    from datetime import datetime, timedelta

    params = config["RULE"]["METRICS"]["PARAMS"]
    date_start = params["date_start"]
    date_end = params["date_end"]
    sale_prob = params["sale_prob"]
    seed = params["seed"]
    granularity = params["granularity"]

    # Extract funnel conversion rates
    impression_to_visit_rate = params["impression_to_visit_rate"]
    visit_to_cart_rate = params["visit_to_cart_rate"]
    cart_to_order_rate = params["cart_to_order_rate"]

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
            # Determine if funnel activity occurs
            funnel_activity = random.random() < sale_prob

            if funnel_activity:
                # Generate funnel metrics top-down
                impressions = random.choices([10, 25, 50, 100, 200], weights=[40, 30, 15, 10, 5])[0]

                visits_base = impressions * impression_to_visit_rate
                visits = max(1, int(visits_base * random.uniform(0.8, 1.2)))

                cart_base = visits * visit_to_cart_rate
                cart_adds = max(0, int(cart_base * random.uniform(0.7, 1.3)))

                order_base = cart_adds * cart_to_order_rate
                order_potential = max(0, int(order_base))

                if order_potential > 0:
                    ordered_units = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
                else:
                    ordered_units = 0

                revenue = round(prod["price"] * ordered_units, 2)

                if ordered_units > 0:
                    average_selling_price = prod["price"]
                else:
                    average_selling_price = 0.0
            else:
                # No funnel activity
                impressions = 0
                visits = 0
                cart_adds = 0
                ordered_units = 0
                revenue = 0.0
                average_selling_price = 0.0

            # Build row with all metrics
            row = prod.to_dict()
            row["date"] = current_date.strftime("%Y-%m-%d")
            row["impressions"] = impressions
            row["visits"] = visits
            row["cart_adds"] = cart_adds
            row["ordered_units"] = ordered_units
            row["revenue"] = revenue
            row["average_selling_price"] = average_selling_price
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

    IMPORTANT: Includes ALL products for ALL weeks, even with zero activity.
    This ensures the weekly DataFrame has the same completeness as daily data.

    Args:
        daily_df: Daily metrics DataFrame with funnel columns
        product_characteristics: Original product characteristics DataFrame

    Returns:
        Weekly aggregated DataFrame with date = week start (Monday)
        Columns: [asin, category, price, date, impressions, visits, cart_adds,
                 ordered_units, revenue, average_selling_price]
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
        {"impressions": "sum", "visits": "sum", "cart_adds": "sum", "ordered_units": "sum", "revenue": "sum"}
    )

    # Merge with complete grid to fill in zero-sale weeks
    weekly = complete_grid.merge(sales_agg, on=["asin", "category", "price", "week_start"], how="left")

    # Fill NaN values with 0 (weeks with no sales)
    weekly["impressions"] = weekly["impressions"].fillna(0).astype(int)
    weekly["visits"] = weekly["visits"].fillna(0).astype(int)
    weekly["cart_adds"] = weekly["cart_adds"].fillna(0).astype(int)
    weekly["ordered_units"] = weekly["ordered_units"].fillna(0).astype(int)
    weekly["revenue"] = weekly["revenue"].fillna(0.0)

    # Calculate average_selling_price for weekly data
    weekly["average_selling_price"] = 0.0
    mask_has_sales = weekly["ordered_units"] > 0
    weekly.loc[mask_has_sales, "average_selling_price"] = (
        weekly.loc[mask_has_sales, "revenue"] / weekly.loc[mask_has_sales, "ordered_units"]
    ).round(2)

    # Convert week_start back to string format YYYY-MM-DD
    weekly["date"] = weekly["week_start"].dt.strftime("%Y-%m-%d")
    weekly = weekly.drop(columns=["week_start"])

    # Reorder columns to match schema
    weekly = weekly[
        [
            "asin",
            "category",
            "price",
            "date",
            "impressions",
            "visits",
            "cart_adds",
            "ordered_units",
            "revenue",
            "average_selling_price",
        ]
    ]

    return weekly
