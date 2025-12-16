"""Enrichment module for applying catalog enrichment treatments to sales data."""

import copy
import importlib
import json
import random
from typing import Any, Callable, Dict, List, Tuple, Union

import pandas as pd


def parse_impact_spec(impact_spec: Dict) -> Tuple[str, str, Dict[str, Any]]:
    """
    Parse IMPACT specification into module, function, and params.

    Supports dict format with capitalized keys:
    {"FUNCTION": "combined_boost", "PARAMS": {"effect_size": 0.5, "ramp_days": 7}}
    {"MODULE": "my_module", "FUNCTION": "my_func", "PARAMS": {...}}

    Args:
        impact_spec: IMPACT specification from config (must be dict)

    Returns:
        Tuple of (module_name, function_name, params_dict)
    """
    if not isinstance(impact_spec, dict):
        raise ValueError(f"IMPACT must be a dict with FUNCTION and PARAMS keys, got {type(impact_spec)}")

    # Dict format with capitalized keys
    module_name = impact_spec.get("MODULE", "enrichment_impact_library")
    function_name = impact_spec.get("FUNCTION")
    params = impact_spec.get("PARAMS", {})

    if not function_name:
        raise ValueError("IMPACT dict must include 'FUNCTION' field")

    return module_name, function_name, params


def assign_enrichment(products: List[Dict], fraction: float, seed: int = None) -> List[Dict]:
    """
    Assign enrichment treatment to a fraction of products.

    Args:
        products: List of product dictionaries
        fraction: Fraction of products to enrich (0.0 to 1.0)
        seed: Random seed for reproducibility

    Returns:
        List of products with added 'enriched' boolean field
    """
    if seed is not None:
        random.seed(seed)

    # Create copy to avoid modifying original
    enriched_products = copy.deepcopy(products)

    # Randomly select products for enrichment
    n_enriched = int(len(products) * fraction)
    enriched_indices = random.sample(range(len(products)), n_enriched)

    # Add enrichment field
    for i, product in enumerate(enriched_products):
        product["enriched"] = i in enriched_indices

    return enriched_products


def load_effect_function(module_name: str, function_name: str) -> Callable:
    """
    Load treatment effect function from module.

    Args:
        module_name: Name of module (e.g., 'enrichment_impact_library' or 'my_custom_effects')
        function_name: Name of function within module

    Returns:
        Treatment effect function
    """
    # Try to import from online_retail_simulator package first
    try:
        module = importlib.import_module(f"online_retail_simulator.{module_name}")
    except (ImportError, ModuleNotFoundError):
        # Fall back to importing as standalone module
        module = importlib.import_module(module_name)

    return getattr(module, function_name)


def apply_enrichment_to_sales(
    sales: List[Dict],
    enriched_products: List[Dict],
    enrichment_start: str,
    effect_function: Callable,
    **kwargs,
) -> List[Dict]:
    """
    Apply enrichment treatment effect to sales data.

    Args:
        sales: List of sale transaction dictionaries
        enriched_products: List of products with 'enriched' field
        enrichment_start: Start date of enrichment (YYYY-MM-DD)
        effect_function: Treatment effect function to apply
        **kwargs: Additional parameters to pass to effect function

    Returns:
        List of modified sales with treatment effect applied
    """
    # Create lookup for enriched products
    enriched_ids = {p["product_id"] for p in enriched_products if p.get("enriched", False)}

    # Apply effect to sales of enriched products
    treated_sales = []
    for sale in sales:
        sale_copy = copy.deepcopy(sale)

        if sale_copy["product_id"] in enriched_ids:
            # Apply treatment effect function with all params as kwargs
            sale_copy = effect_function(sale_copy, enrichment_start=enrichment_start, **kwargs)

        treated_sales.append(sale_copy)

    return treated_sales


# High-level enrichment interface similar to 'simulate'
def enrich(config_path: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply enrichment to a DataFrame using a config file.
    Args:
        config_path: Path to enrichment config (YAML or JSON)
        df: DataFrame with sales data (must include asin)
    Returns:
        DataFrame with enrichment applied (factual version)
    """
    from pathlib import Path

    import yaml

    # Load config - support both YAML and JSON
    config_file = Path(config_path)
    with open(config_file, "r") as f:
        if config_file.suffix.lower() in [".yaml", ".yml"]:
            config = yaml.safe_load(f)
        else:
            config = json.load(f)

    # Get impact specification from config
    impact_spec = config.get("IMPACT")
    if not impact_spec:
        raise ValueError("Config must include 'IMPACT' specification")

    # Parse impact function
    module_name, function_name, all_params = parse_impact_spec(impact_spec)
    impact_function = load_effect_function(module_name, function_name)

    # Get product list from df - use asin as product identifier
    if "asin" not in df.columns:
        raise ValueError("Input DataFrame must contain 'asin' column")

    # Convert DataFrame to list of dicts for sales, mapping asin to product_id
    sales = df.to_dict(orient="records")
    for sale in sales:
        sale["product_id"] = sale["asin"]  # Map asin to product_id for enrichment
        if "price" in sale and "unit_price" not in sale:
            sale["unit_price"] = sale["price"]  # Ensure unit_price exists

    # Apply impact function with all parameters - let the function handle everything
    treated_sales = impact_function(sales, **all_params)

    # Convert back to DataFrame and clean up
    for sale in treated_sales:
        sale.pop("product_id", None)  # Remove temporary product_id mapping
        sale.pop("unit_price", None) if "price" in sale else None  # Remove duplicate price field

    enriched_df = pd.DataFrame(treated_sales)

    # Preserve original column order
    original_cols = [col for col in df.columns if col in enriched_df.columns]
    new_cols = [col for col in enriched_df.columns if col not in df.columns]
    enriched_df = enriched_df[original_cols + new_cols]

    return enriched_df
