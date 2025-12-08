"""Main simulator interface for generating and exporting retail data."""

import json
from pathlib import Path
from typing import List, Dict, Optional

from .simulator_product_data import generate_product_data
from .simulator_product_sales import generate_sales_data


def generate_products(n_products: int = 100, seed: Optional[int] = None) -> List[Dict]:
    """
    Generate synthetic product catalog.
    
    Args:
        n_products: Number of products to generate (default: 100)
        seed: Random seed for reproducibility (default: None)
    
    Returns:
        List of product dictionaries
    """
    return generate_product_data(n_products=n_products, seed=seed)


def generate_sales(
    products: List[Dict],
    n_transactions: int = 500,
    days_back: int = 30,
    seed: Optional[int] = None
) -> List[Dict]:
    """
    Generate synthetic sales transactions from products.
    
    Args:
        products: List of product dictionaries
        n_transactions: Number of transactions to generate (default: 500)
        days_back: Number of days to spread transactions over (default: 30)
        seed: Random seed for reproducibility (default: None)
    
    Returns:
        List of sales transaction dictionaries
    """
    return generate_sales_data(
        products=products,
        n_transactions=n_transactions,
        days_back=days_back,
        seed=seed
    )


def save_to_json(data: List[Dict], filepath: str, indent: int = 2) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: List of dictionaries to save
        filepath: Path to output JSON file
        indent: Indentation level for pretty printing (default: 2)
    """
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=indent)
    
    print(f"Data saved to {filepath}")
