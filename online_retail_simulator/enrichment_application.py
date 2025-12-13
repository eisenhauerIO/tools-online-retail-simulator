"""Enrichment module for applying catalog enrichment treatments to sales data."""

import random
import importlib
import json
import copy
from pathlib import Path
from typing import List, Dict, Callable, Union, Tuple, Any

import pandas as pd


def parse_effect_spec(effect_spec: Union[str, Dict]) -> Tuple[str, str, Dict[str, Any]]:
    """
    Parse EFFECT specification into module, function, and params.
    
    Supports three formats:
    1. Shorthand string: "quantity_boost:0.5" -> function_name:effect_size
    2. Dict format: {"function": "combined_boost", "params": {"effect_size": 0.5, "ramp_days": 7}}
    3. Dict with module: {"module": "my_module", "function": "my_func", "params": {...}}
    
    Args:
        effect_spec: EFFECT specification from config
    
    Returns:
        Tuple of (module_name, function_name, params_dict)
    """
    if isinstance(effect_spec, str):
        # Shorthand format: "function_name:effect_size"
        if ":" in effect_spec:
            function_name, effect_size_str = effect_spec.split(":", 1)
            return "enrichment_impact_library", function_name.strip(), {"effect_size": float(effect_size_str)}
        else:
            # Just function name, no params
            return "enrichment_impact_library", effect_spec.strip(), {}
    
    elif isinstance(effect_spec, dict):
        # Dict format
        module_name = effect_spec.get("module", "enrichment_impact_library")
        function_name = effect_spec.get("function")
        params = effect_spec.get("params", {})
        
        if not function_name:
            raise ValueError("EFFECT dict must include 'function' field")
        
        return module_name, function_name, params
    
    else:
        raise ValueError(f"EFFECT must be string or dict, got {type(effect_spec)}")


def assign_enrichment(
    products: List[Dict],
    fraction: float,
    seed: int = None
) -> List[Dict]:
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
        product['enriched'] = i in enriched_indices
    
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
        module = importlib.import_module(f'online_retail_simulator.{module_name}')
    except (ImportError, ModuleNotFoundError):
        # Fall back to importing as standalone module
        module = importlib.import_module(module_name)
    
    return getattr(module, function_name)


def apply_enrichment_to_sales(
    sales: List[Dict],
    enriched_products: List[Dict],
    enrichment_start: str,
    effect_function: Callable,
    **kwargs
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
    enriched_ids = {p['product_id'] for p in enriched_products if p.get('enriched', False)}
    
    # Apply effect to sales of enriched products
    treated_sales = []
    for sale in sales:
        sale_copy = copy.deepcopy(sale)
        
        if sale_copy['product_id'] in enriched_ids:
            # Apply treatment effect function with all params as kwargs
            sale_copy = effect_function(
                sale_copy,
                enrichment_start=enrichment_start,
                **kwargs
            )
        
        treated_sales.append(sale_copy)
    
    return treated_sales


# High-level enrichment interface similar to 'simulate'
def enrich(config_path: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply enrichment to a DataFrame using a config file.
    Args:
        config_path: Path to enrichment config (JSON)
        df: DataFrame with sales data (must include product_id)
    Returns:
        DataFrame with enrichment applied (factual version)
    """
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Get enrichment parameters from config
    effect_spec = config.get('EFFECT')
    enrichment_fraction = config.get('ENRICHMENT_FRACTION', 0.5)
    enrichment_start = config.get('ENRICHMENT_START', '2020-01-01')
    seed = config.get('SEED', None)

    # Get product list from df
    if 'product_id' not in df.columns:
        raise ValueError("Input DataFrame must contain 'product_id' column")
    products = (
        df[['product_id']]
        .drop_duplicates()
        .to_dict(orient='records')
    )

    # Assign enrichment
    enriched_products = assign_enrichment(products, enrichment_fraction, seed=seed)

    # Parse effect function
    module_name, function_name, params = parse_effect_spec(effect_spec)
    effect_function = load_effect_function(module_name, function_name)

    # Convert DataFrame to list of dicts for sales
    sales = df.to_dict(orient='records')

    # Apply enrichment
    treated_sales = apply_enrichment_to_sales(
        sales,
        enriched_products,
        enrichment_start,
        effect_function,
        **params
    )

    # Convert back to DataFrame
    enriched_df = pd.DataFrame(treated_sales)
    # Preserve original column order if possible
    enriched_df = enriched_df[df.columns.intersection(enriched_df.columns)]
    # Add any new columns at the end
    for col in enriched_df.columns:
        if col not in df.columns:
            enriched_df[col] = enriched_df[col]
    return enriched_df
