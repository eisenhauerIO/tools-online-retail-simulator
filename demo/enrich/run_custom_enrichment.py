"""
Example demonstrating custom enrichment with price discount function.

This script shows:
1. Definition of a custom enrichment function
2. Registration and usage of the custom function
3. Price-based treatment effects (vs ordered_units-based defaults)
"""

import copy
from datetime import datetime
from typing import Dict, List

import numpy as np

from online_retail_simulator import enrich, load_job_results, register_enrichment_function, simulate


def price_discount(metrics: List[Dict], **kwargs) -> List[Dict]:
    """
    Apply price discount to enriched products.

    Args:
        metrics: List of metric record dictionaries
        **kwargs: Parameters including:
            - discount_percent: Percentage discount (default: 0.2 for 20% off)
            - enrichment_fraction: Fraction of products to enrich (default: 0.3)
            - enrichment_start: Start date of enrichment (default: "2024-11-15")
            - seed: Random seed for product selection (default: 42)

    Returns:
        List of modified metric dictionaries with price discount applied
    """
    discount_percent = kwargs.get("discount_percent", 0.2)
    enrichment_fraction = kwargs.get("enrichment_fraction", 0.3)
    enrichment_start = kwargs.get("enrichment_start", "2024-11-15")
    seed = kwargs.get("seed", 42)

    rng = np.random.default_rng(seed)

    # Get unique products and select fraction for enrichment
    unique_products = list(set(record["product_id"] for record in metrics))
    n_enriched = int(len(unique_products) * enrichment_fraction)
    enriched_product_ids = set(rng.choice(unique_products, size=n_enriched, replace=False))

    # Apply discount to enriched products after start date
    treated_metrics = []
    start_date = datetime.strptime(enrichment_start, "%Y-%m-%d")

    for record in metrics:
        record_copy = copy.deepcopy(record)
        record_date = datetime.strptime(record_copy["date"], "%Y-%m-%d")

        # Apply discount if product is enriched and date is after start
        if record_copy["product_id"] in enriched_product_ids and record_date >= start_date:
            unit_price = record_copy.get("unit_price", record_copy.get("price"))
            discounted_price = unit_price * (1 - discount_percent)

            # Update price fields
            if "unit_price" in record_copy:
                record_copy["unit_price"] = round(discounted_price, 2)
            if "price" in record_copy:
                record_copy["price"] = round(discounted_price, 2)

            # Recalculate revenue
            record_copy["revenue"] = round(record_copy["ordered_units"] * discounted_price, 2)

        treated_metrics.append(record_copy)

    return treated_metrics


def main():
    print("\n" + "=" * 60)
    print("CUSTOM ENRICHMENT DEMO")
    print("=" * 60)
    print("Using custom 'price_discount' function for promotional analysis\n")

    # Step 1: Register custom function
    print("Step 1: Registering custom enrichment function...")
    register_enrichment_function("price_discount", price_discount)
    print("✓ Registered 'price_discount' function")

    # Step 2: Generate base simulation data
    print("\nStep 2: Generating base simulation data...")
    job_info = simulate("../simulate/config_default_simulation.yaml")
    print(f"✓ Simulation completed. Job ID: {job_info}")

    # Load simulation results
    metrics_df = load_job_results(job_info)["metrics"]
    print(f"✓ Generated {len(metrics_df)} metrics records")
    print(f"✓ Date range: {metrics_df['date'].min()} to {metrics_df['date'].max()}")
    print(f"✓ Products: {metrics_df['product_identifier'].nunique()} unique products")

    # Step 3: Apply custom enrichment
    print("\nStep 3: Applying custom enrichment (price_discount)...")
    enriched_job_info = enrich("config_custom_enrichment.yaml", job_info)
    print(f"✓ Enrichment completed. Job ID: {enriched_job_info}")
    print("✓ Uses 25% price discount on 40% of products")

    # Load enriched results
    enriched_df = load_job_results(enriched_job_info)["enriched"]
    print(f"✓ Applied enrichment to {len(enriched_df)} metrics records")

    # Step 4: Compare results
    print("\nStep 4: Comparing results...")
    enrichment_start = "2024-11-15"
    original_post = metrics_df[metrics_df["date"] >= enrichment_start]
    enriched_post = enriched_df[enriched_df["date"] >= enrichment_start]

    print(f"\nPost-enrichment period ({enrichment_start} onwards):")
    print(f"Original total ordered_units: {original_post['ordered_units'].sum()}")
    print(f"Enriched total ordered_units: {enriched_post['ordered_units'].sum()}")
    print(
        f"Quantity change: {((enriched_post['ordered_units'].sum() / original_post['ordered_units'].sum()) - 1) * 100:+.1f}%"
    )

    print(f"\nOriginal total revenue: ${original_post['revenue'].sum():.2f}")
    print(f"Enriched total revenue: ${enriched_post['revenue'].sum():.2f}")
    print(
        f"Revenue change: {((enriched_post['revenue'].sum() / original_post['revenue'].sum()) - 1) * 100:+.1f}%"
    )

    # Show average price change
    original_avg_price = (original_post["revenue"] / original_post["ordered_units"]).mean()
    enriched_avg_price = (enriched_post["revenue"] / enriched_post["ordered_units"]).mean()
    print(
        f"\nAverage unit price: ${original_avg_price:.2f} → ${enriched_avg_price:.2f}"
    )
    print(
        f"Price change: {((enriched_avg_price / original_avg_price) - 1) * 100:+.1f}%"
    )

    print(f"\n✓ Results saved to: {job_info.storage_path}/{job_info.job_id}/")

    print("\n" + "=" * 60)
    print("Custom enrichment complete!")
    print("=" * 60)
    print("This demonstrates custom price-based treatment effects")
    print("for promotional campaigns and price elasticity analysis.\n")


if __name__ == "__main__":
    main()
