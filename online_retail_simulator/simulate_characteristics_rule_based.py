"""
Rule-based product characteristics simulation.
"""
import random
import pandas as pd
from typing import List, Dict, Optional

# Constants copied from simulator_rule_based.py
_CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Books",
    "Sports & Outdoors",
    "Toys & Games",
    "Food & Beverage",
    "Health & Beauty"
]

_PRODUCT_NAMES = {
    "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "Monitor", "Keyboard", "Mouse", "Webcam"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sweater", "Dress", "Shorts", "Hoodie", "Socks"],
    "Home & Garden": ["Chair", "Table", "Lamp", "Rug", "Curtains", "Vase", "Mirror", "Clock"],
    "Books": ["Novel", "Textbook", "Cookbook", "Biography", "Comic", "Magazine", "Journal", "Guide"],
    "Sports & Outdoors": ["Ball", "Bike", "Tent", "Backpack", "Yoga Mat", "Weights", "Running Shoes", "Water Bottle"],
    "Toys & Games": ["Board Game", "Puzzle", "Action Figure", "Doll", "Building Blocks", "Card Game", "Stuffed Animal", "Remote Car"],
    "Food & Beverage": ["Coffee", "Tea", "Snacks", "Chocolate", "Juice", "Cookies", "Nuts", "Energy Bar"],
    "Health & Beauty": ["Shampoo", "Lotion", "Soap", "Toothpaste", "Perfume", "Makeup", "Vitamins", "Sunscreen"]
}

_PRICE_RANGES = {
    "Electronics": (50, 1500),
    "Clothing": (15, 200),
    "Home & Garden": (20, 500),
    "Books": (10, 60),
    "Sports & Outdoors": (15, 300),
    "Toys & Games": (10, 100),
    "Food & Beverage": (5, 50),
    "Health & Beauty": (8, 80)
}



def simulate_characteristics_rule_based(config_path: str, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Generate synthetic product characteristics (rule-based).
    Args:
        config_path: Path to JSON configuration file
        config: Optional pre-loaded config (avoids re-reading)
    Returns:
        DataFrame of product characteristics
    """
    from .config_processor import process_config
    if config is None:
        config = process_config(config_path)
    rule_config = config["RULE"]
    seed = config.get("SEED", 42)
    num_products = rule_config.get("NUM_PRODUCTS", 100)
    if seed is not None:
        random.seed(seed)
    products: List[Dict] = []
    for i in range(num_products):
        category = random.choice(_CATEGORIES)
        product_name = random.choice(_PRODUCT_NAMES[category])
        price_min, price_max = _PRICE_RANGES[category]
        price = round(random.uniform(price_min, price_max), 2)
        products.append({
            "product_id": f"PROD{i+1:04d}",
            "name": product_name,
            "category": category,
            "price": price
        })
    return pd.DataFrame(products)
