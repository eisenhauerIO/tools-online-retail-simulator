"""Library of predefined treatment effect functions for catalog enrichment."""

import copy
import random
from datetime import datetime

import pandas as pd


def quantity_boost(sales: list, **kwargs) -> list:
    """
    Boost ordered units by a percentage for enriched products.

    Args:
        sales: List of sale transaction dictionaries
        **kwargs: Parameters including:
            - effect_size: Percentage increase in ordered units (default: 0.5 for 50% boost)
            - enrichment_fraction: Fraction of products to enrich (default: 0.3)
            - enrichment_start: Start date of enrichment (default: "2024-11-15")
            - seed: Random seed for product selection (default: 42)

    Returns:
        List of modified sale dictionaries with treatment applied
    """
    effect_size = kwargs.get("effect_size", 0.5)
    enrichment_fraction = kwargs.get("enrichment_fraction", 0.3)
    enrichment_start = kwargs.get("enrichment_start", "2024-11-15")
    seed = kwargs.get("seed", 42)

    if seed is not None:
        random.seed(seed)

    unique_products = list(set(sale["product_id"] for sale in sales))
    n_enriched = int(len(unique_products) * enrichment_fraction)
    enriched_product_ids = set(random.sample(unique_products, n_enriched))

    treated_sales = []
    start_date = datetime.strptime(enrichment_start, "%Y-%m-%d")

    for sale in sales:
        sale_copy = copy.deepcopy(sale)
        sale_date = datetime.strptime(sale_copy["date"], "%Y-%m-%d")

        is_enriched = sale_copy["product_id"] in enriched_product_ids
        sale_copy["enriched"] = is_enriched

        if is_enriched and sale_date >= start_date:
            original_quantity = sale_copy["ordered_units"]
            sale_copy["ordered_units"] = int(original_quantity * (1 + effect_size))
            unit_price = sale_copy.get("unit_price", sale_copy.get("price"))
            sale_copy["revenue"] = round(sale_copy["ordered_units"] * unit_price, 2)

        treated_sales.append(sale_copy)

    return treated_sales


def probability_boost(sales: list, **kwargs) -> list:
    """
    Boost sale probability (simulated by ordered units increase as proxy).

    Args:
        sales: List of sale transaction dictionaries
        **kwargs: Same parameters as quantity_boost

    Returns:
        List of modified sale dictionaries
    """
    return quantity_boost(sales, **kwargs)


def product_detail_boost(sales: list, **kwargs) -> list:
    """
    Product detail regeneration and sales boost for enrichment experiments.

    Selects a fraction of products for treatment, regenerates their product
    details (title, description, features) while preserving brand/category/price,
    and applies sales boost effect.

    Args:
        sales: List of sale transaction dictionaries
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
        List of modified sale dictionaries with treatment applied
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

    if seed is not None:
        random.seed(seed)

    # 1. Save original product details
    if job_info and products:
        job_info.save_df("product_details_original", pd.DataFrame(products))

    # 2. Select treatment products
    if products:
        unique_product_ids = list(set(p.get("product_identifier", p.get("product_id")) for p in products))
    else:
        unique_product_ids = list(set(sale["product_id"] for sale in sales))

    n_treatment = int(len(unique_product_ids) * enrichment_fraction)
    treatment_ids = set(random.sample(unique_product_ids, n_treatment))

    # 3. Regenerate product details for treatment products
    if products and job_info:
        updated_products = _regenerate_product_details(products, treatment_ids, prompt_path, backend, seed)
        job_info.save_df("product_details_enriched", pd.DataFrame(updated_products))

    # 4. Apply sales boost effect
    treated_sales = []
    start_date = datetime.strptime(enrichment_start, "%Y-%m-%d")

    for sale in sales:
        sale_copy = copy.deepcopy(sale)
        product_id = sale_copy.get("product_id", sale_copy.get("product_identifier"))
        sale_date = datetime.strptime(sale_copy["date"], "%Y-%m-%d")

        is_enriched = product_id in treatment_ids
        sale_copy["enriched"] = is_enriched

        if is_enriched and sale_date >= start_date:
            days_since_start = (sale_date - start_date).days
            ramp_factor = 1.0 if ramp_days <= 0 else min(1.0, days_since_start / ramp_days)
            adjusted_effect = effect_size * ramp_factor

            original_quantity = sale_copy["ordered_units"]
            sale_copy["ordered_units"] = int(original_quantity * (1 + adjusted_effect))
            unit_price = sale_copy.get("unit_price", sale_copy.get("price"))
            sale_copy["revenue"] = round(sale_copy["ordered_units"] * unit_price, 2)

        treated_sales.append(sale_copy)

    return treated_sales


def _regenerate_product_details(
    products: list,
    treatment_ids: set,
    prompt_path: str,
    backend: str,
    seed: int,
) -> list:
    """
    Regenerate product details for treatment products.

    Preserves: brand, category, price
    Regenerates: title, description, features
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
        treatment_products = regenerated_df.to_dict("records")

    return control_products + treatment_products
