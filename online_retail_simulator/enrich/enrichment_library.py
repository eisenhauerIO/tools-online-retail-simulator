"""Library of predefined treatment effect functions for catalog enrichment."""

import copy
from datetime import datetime

import numpy as np
import pandas as pd


def quantity_boost(metrics: list, **kwargs) -> tuple:
    """
    Boost ordered units by a percentage for enriched products.

    Args:
        metrics: List of metric record dictionaries
        **kwargs: Parameters including:
            - effect_size: Percentage increase in ordered units (default: 0.5 for 50% boost)
            - enrichment_fraction: Fraction of products to enrich (default: 0.3)
            - enrichment_start: Start date of enrichment (default: "2024-11-15")
            - seed: Random seed for product selection (default: 42)
            - min_units: Minimum units for enriched products with zero sales (default: 1)

    Returns:
        Tuple of (treated_metrics, potential_outcomes_df):
            - treated_metrics: List of modified metric dictionaries with treatment applied
            - potential_outcomes_df: DataFrame with Y0_revenue and Y1_revenue for all products
    """
    effect_size = kwargs.get("effect_size", 0.5)
    enrichment_fraction = kwargs.get("enrichment_fraction", 0.3)
    enrichment_start = kwargs.get("enrichment_start", "2024-11-15")
    seed = kwargs.get("seed", 42)
    min_units = kwargs.get("min_units", 1)

    rng = np.random.default_rng(seed)

    unique_products = list(set(record["product_id"] for record in metrics))
    n_enriched = int(len(unique_products) * enrichment_fraction)
    enriched_product_ids = set(rng.choice(unique_products, size=n_enriched, replace=False))

    treated_metrics = []
    potential_outcomes = {}  # {(product_id, date): {'Y0_revenue': x, 'Y1_revenue': y}}
    start_date = datetime.strptime(enrichment_start, "%Y-%m-%d")

    for record in metrics:
        record_copy = copy.deepcopy(record)
        product_id = record_copy["product_id"]
        record_date_str = record_copy["date"]
        record_date = datetime.strptime(record_date_str, "%Y-%m-%d")

        is_enriched = product_id in enriched_product_ids
        record_copy["enriched"] = is_enriched

        # Calculate Y(0) - baseline revenue (no treatment)
        y0_revenue = record_copy["revenue"]

        # Calculate Y(1) - revenue if treated (for ALL products)
        unit_price = record_copy.get("unit_price", record_copy.get("price"))
        if record_date >= start_date:
            original_quantity = record_copy["ordered_units"]
            boosted_quantity = int(original_quantity * (1 + effect_size))
            boosted_quantity = max(min_units, boosted_quantity)
            y1_revenue = round(boosted_quantity * unit_price, 2)
        else:
            # Before treatment start, Y(1) = Y(0)
            y1_revenue = y0_revenue

        # Store potential outcomes for ALL products
        key = (product_id, record_date_str)
        potential_outcomes[key] = {"Y0_revenue": y0_revenue, "Y1_revenue": y1_revenue}

        # Apply factual outcome (only for treated products)
        if is_enriched and record_date >= start_date:
            record_copy["ordered_units"] = boosted_quantity
            record_copy["revenue"] = y1_revenue

        treated_metrics.append(record_copy)

    # Build potential outcomes DataFrame
    potential_outcomes_df = pd.DataFrame(
        [
            {
                "product_identifier": pid,
                "date": d,
                "Y0_revenue": v["Y0_revenue"],
                "Y1_revenue": v["Y1_revenue"],
            }
            for (pid, d), v in potential_outcomes.items()
        ]
    )

    return treated_metrics, potential_outcomes_df


def probability_boost(metrics: list, **kwargs) -> tuple:
    """
    Boost sale probability (simulated by ordered units increase as proxy).

    Args:
        metrics: List of metric record dictionaries
        **kwargs: Same parameters as quantity_boost

    Returns:
        Tuple of (treated_metrics, potential_outcomes_df) - same as quantity_boost
    """
    return quantity_boost(metrics, **kwargs)


def product_detail_boost(metrics: list, **kwargs) -> tuple:
    """
    Product detail regeneration and metrics boost for enrichment experiments.

    Selects a fraction of products for treatment, regenerates their product
    details (title, description, features) while preserving brand/category/price,
    and applies metrics boost effect.

    Args:
        metrics: List of metric record dictionaries
        **kwargs: Parameters including:
            - job_info: JobInfo for saving product artifacts (required for saving)
            - products: List of product dictionaries (required for product details)
            - effect_size: Percentage increase in ordered units (default: 0.5)
            - ramp_days: Number of days for ramp-up period (default: 7)
            - enrichment_fraction: Fraction of products to enrich (default: 0.3)
            - enrichment_start: Start date of enrichment (default: "2024-11-15")
            - seed: Random seed for product selection (default: 42)
            - prompt_path: Path to custom prompt template file (optional)
            - backend: Backend to use for regeneration ("mock" or "ollama", default: "mock")

    Returns:
        Tuple of (treated_metrics, potential_outcomes_df):
            - treated_metrics: List of modified metric dictionaries with treatment applied
            - potential_outcomes_df: DataFrame with Y0_revenue and Y1_revenue for all products
    """
    job_info = kwargs.get("job_info")
    products = kwargs.get("products")
    effect_size = kwargs.get("effect_size", 0.5)
    ramp_days = kwargs.get("ramp_days", 7)
    enrichment_fraction = kwargs.get("enrichment_fraction", 0.3)
    enrichment_start = kwargs.get("enrichment_start", "2024-11-15")
    seed = kwargs.get("seed", 42)
    prompt_path = kwargs.get("prompt_path")
    backend = kwargs.get("backend", "mock")
    quality_boost = kwargs.get("quality_boost", 0.0)

    rng = np.random.default_rng(seed)

    # 1. Save original product details
    if job_info and products:
        job_info.save_df("product_details_original", pd.DataFrame(products))

    # 2. Select treatment products
    if products:
        unique_product_ids = list(set(p.get("product_identifier", p.get("product_id")) for p in products))
    else:
        unique_product_ids = list(set(record["product_id"] for record in metrics))

    n_treatment = int(len(unique_product_ids) * enrichment_fraction)
    treatment_ids = set(rng.choice(unique_product_ids, size=n_treatment, replace=False))

    # 3. Regenerate product details for treatment products
    if products and job_info:
        updated_products = _regenerate_product_details(
            products, treatment_ids, prompt_path, backend, seed, quality_boost
        )
        job_info.save_df("product_details_enriched", pd.DataFrame(updated_products))

    # 4. Apply metrics boost effect and calculate potential outcomes
    treated_metrics = []
    potential_outcomes = {}  # {(product_id, date): {'Y0_revenue': x, 'Y1_revenue': y}}
    start_date = datetime.strptime(enrichment_start, "%Y-%m-%d")

    for record in metrics:
        record_copy = copy.deepcopy(record)
        product_id = record_copy.get("product_id", record_copy.get("product_identifier"))
        record_date_str = record_copy["date"]
        record_date = datetime.strptime(record_date_str, "%Y-%m-%d")

        is_enriched = product_id in treatment_ids
        record_copy["enriched"] = is_enriched

        # Calculate Y(0) - baseline revenue (no treatment)
        y0_revenue = record_copy["revenue"]

        # Calculate Y(1) - revenue if treated (for ALL products, with ramp-up)
        unit_price = record_copy.get("unit_price", record_copy.get("price"))
        if record_date >= start_date:
            days_since_start = (record_date - start_date).days
            ramp_factor = 1.0 if ramp_days <= 0 else min(1.0, days_since_start / ramp_days)
            adjusted_effect = effect_size * ramp_factor

            original_quantity = record_copy["ordered_units"]
            boosted_quantity = int(original_quantity * (1 + adjusted_effect))
            y1_revenue = round(boosted_quantity * unit_price, 2)
        else:
            # Before treatment start, Y(1) = Y(0)
            y1_revenue = y0_revenue

        # Store potential outcomes for ALL products
        key = (product_id, record_date_str)
        potential_outcomes[key] = {"Y0_revenue": y0_revenue, "Y1_revenue": y1_revenue}

        # Apply factual outcome (only for treated products)
        if is_enriched and record_date >= start_date:
            record_copy["ordered_units"] = boosted_quantity
            record_copy["revenue"] = y1_revenue

        treated_metrics.append(record_copy)

    # Build potential outcomes DataFrame
    potential_outcomes_df = pd.DataFrame(
        [
            {
                "product_identifier": pid,
                "date": d,
                "Y0_revenue": v["Y0_revenue"],
                "Y1_revenue": v["Y1_revenue"],
            }
            for (pid, d), v in potential_outcomes.items()
        ]
    )

    return treated_metrics, potential_outcomes_df


def _regenerate_product_details(
    products: list,
    treatment_ids: set,
    prompt_path: str,
    backend: str,
    seed: int,
    quality_boost: float,
) -> list:
    """
    Regenerate product details for treatment products.

    Preserves: brand, category, price
    Regenerates: title, description, features
    Updates: quality_score (recalculated + optional boost)

    Args:
        products: List of product dictionaries
        treatment_ids: Set of product IDs to treat
        prompt_path: Path to custom prompt template
        backend: Backend to use ("mock" or "ollama")
        seed: Random seed
        quality_boost: Additional quality score boost for treated products (0.0-1.0)
    """
    control_products = []
    treatment_products = []

    for product in products:
        product_copy = copy.deepcopy(product)
        product_id = product_copy.get("product_identifier", product_copy.get("product_id"))

        if product_id in treatment_ids:
            product_copy["enriched"] = True
            treatment_products.append(product_copy)
        else:
            product_copy["enriched"] = False
            control_products.append(product_copy)

    if treatment_products:
        treatment_df = pd.DataFrame(treatment_products)

        if backend == "ollama":
            from ..simulate.product_details_ollama import simulate_product_details_ollama

            regenerated_df = simulate_product_details_ollama(treatment_df, prompt_path=prompt_path)
        else:  # mock
            from ..simulate.product_details_mock import simulate_product_details_mock

            regenerated_df = simulate_product_details_mock(
                treatment_df, seed=seed, prompt_path=prompt_path, treatment_mode=True
            )

        regenerated_df["enriched"] = True

        # Apply quality boost for treated products (0.0 = no boost)
        regenerated_df["quality_score"] = regenerated_df["quality_score"].apply(lambda x: min(x + quality_boost, 1.0))

        treatment_products = regenerated_df.to_dict("records")

    return control_products + treatment_products
