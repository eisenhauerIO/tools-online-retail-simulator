"""
Example demonstrating default simulation using built-in rule-based generation.

This script shows:
1. Basic product catalog generation across multiple categories
2. Daily and weekly sales transaction simulation
3. Built-in rule-based approach with configurable parameters
4. Customer journey funnel metrics (impressions → visits → cart adds → orders)
"""

import pandas as pd
import yaml

from online_retail_simulator import load_job_results, simulate


def analyze_results(metrics_df, products_df, granularity, job_info):
    """Display analysis for the given granularity.

    Args:
        metrics_df: Metrics DataFrame
        products_df: Products DataFrame
        granularity: "daily" or "weekly"
        job_info: Job information object
    """
    print(f"✓ Generated {len(metrics_df)} metrics records")
    print(f"✓ Date range: {metrics_df['date'].min()} to {metrics_df['date'].max()}")
    print(f"✓ Products: {metrics_df['product_identifier'].nunique()} unique products")
    print(f"✓ Categories: {metrics_df['category'].nunique()} different categories")

    # Granularity-specific info
    if granularity == "weekly":
        dates_dt = pd.to_datetime(metrics_df["date"])
        all_mondays = all(dates_dt.dt.weekday == 0)
        print(f"✓ All dates are Mondays (ISO week start): {all_mondays}")
        print(f"✓ Number of weeks: {metrics_df['date'].nunique()}")
    else:
        print(f"✓ Number of days: {metrics_df['date'].nunique()}")

    # Show category breakdown
    print(f"\nCategory breakdown:")
    category_counts = metrics_df["category"].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count} records")

    # Show funnel metrics and revenue summary
    print(f"\nFunnel metrics:")
    print(f"  Total impressions: {metrics_df['impressions'].sum():,}")
    print(f"  Total visits: {metrics_df['visits'].sum():,}")
    print(f"  Total cart adds: {metrics_df['cart_adds'].sum():,}")
    print(f"  Total ordered units: {metrics_df['ordered_units'].sum():,}")

    # Calculate conversion rates
    if metrics_df['impressions'].sum() > 0:
        conversion_rate = metrics_df['ordered_units'].sum() / metrics_df['impressions'].sum()
        print(f"  Overall conversion rate: {conversion_rate:.2%}")

    print(f"\nRevenue summary:")
    print(
        f"  Price range: ${metrics_df['price'].min():.2f} - ${metrics_df['price'].max():.2f}"
    )
    print(f"  Total revenue: ${metrics_df['revenue'].sum():,.2f}")
    print(f"  Average order value: ${metrics_df['revenue'].mean():.2f}")

    print(f"\n✓ Results saved to: {job_info.storage_path}/{job_info.job_id}/")


def main():
    granularities = ["daily", "weekly"]

    for granularity in granularities:
        print("\n" + "=" * 60)
        print(f"DEFAULT SIMULATION DEMO - {granularity.upper()} GRANULARITY")
        print("=" * 60)
        print(f"Using built-in rule-based generation with {granularity} aggregation\n")

        # Load base config
        config = yaml.safe_load(open("config_default_simulation.yaml"))

        # Set granularity
        config["RULE"]["METRICS"]["PARAMS"]["granularity"] = granularity

        # Update storage path to separate daily and weekly outputs
        config["STORAGE"]["PATH"] = f"output/sim_demo_{granularity}"

        # Save temporary config
        temp_config_path = f"/tmp/config_demo_{granularity}.yaml"
        with open(temp_config_path, "w") as f:
            yaml.dump(config, f)

        # Generate simulation data
        print(f"Generating synthetic retail data ({granularity})...")
        job_info = simulate(temp_config_path)
        print(f"✓ Simulation completed. Job ID: {job_info}")

        # Load results for analysis
        results = load_job_results(job_info)
        products_df = results["products"]
        metrics_df = results["metrics"]

        # Display analysis
        analyze_results(metrics_df, products_df, granularity, job_info)

    print("\n" + "=" * 60)
    print("Default simulation complete!")
    print("=" * 60)
    print("This demonstrates the built-in rule-based generation")
    print("with diverse product categories and realistic funnel metrics.")
    print("\nBoth daily and weekly granularities have been generated,")
    print("allowing you to choose the appropriate level of detail")
    print("for your analysis.\n")


if __name__ == "__main__":
    main()
