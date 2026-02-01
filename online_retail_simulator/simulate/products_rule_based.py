"""
Rule-based product simulation.
"""

import string
from typing import Dict, List

import numpy as np
import pandas as pd


def generate_random_product_identifier(rng: np.random.Generator, prefix: str = "B") -> str:
    """Generate a random product identifier.
    - 10 characters total
    - Alphanumeric
    - Defaults to starting with 'B'
    """
    chars = list(string.ascii_uppercase + string.digits)
    return prefix + "".join(rng.choice(chars) for _ in range(9))


_CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Books",
    "Sports & Outdoors",
    "Toys & Games",
    "Food & Beverage",
    "Health & Beauty",
]

_PRICE_RANGES = {
    "Electronics": (50, 1500),
    "Clothing": (15, 200),
    "Home & Garden": (20, 500),
    "Books": (10, 60),
    "Sports & Outdoors": (15, 300),
    "Toys & Games": (10, 100),
    "Food & Beverage": (5, 50),
    "Health & Beauty": (8, 80),
}


def simulate_products_rule_based(config: Dict) -> pd.DataFrame:
    """
    Generate synthetic products (rule-based).
    Args:
        config: Complete configuration dictionary
    Returns:
        DataFrame of products
    """
    params = config["RULE"]["PRODUCTS"]["PARAMS"]
    num_products, seed = params["num_products"], params["seed"]

    rng = np.random.default_rng(seed)
    products: List[Dict] = []
    for i in range(num_products):
        category = rng.choice(_CATEGORIES)
        price_min, price_max = _PRICE_RANGES[category]
        price = round(rng.uniform(price_min, price_max), 2)
        products.append(
            {
                "product_identifier": generate_random_product_identifier(rng),
                "category": category,
                "price": price,
            }
        )
    return pd.DataFrame(products)
