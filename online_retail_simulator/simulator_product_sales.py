"""Generate synthetic sales data."""

import random
from datetime import datetime, timedelta
from typing import List, Dict


def generate_sales_data(
    products: List[Dict],
    n_transactions: int = 500,
    days_back: int = 30,
    seed: int = None
) -> List[Dict]:
    """
    Generate synthetic sales transactions from product data.
    
    Args:
        products: List of product dictionaries (from simulator_product_data)
        n_transactions: Number of transactions to generate (default: 500)
        days_back: Number of days to spread transactions over (default: 30)
        seed: Random seed for reproducibility (default: None)
    
    Returns:
        List of sales transaction dictionaries
    """
    if seed is not None:
        random.seed(seed)
    
    sales = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    for i in range(n_transactions):
        # Select random product
        product = random.choice(products)
        
        # Generate quantity (favor smaller quantities)
        quantity = random.choices(
            [1, 2, 3, 4, 5],
            weights=[50, 25, 15, 7, 3]
        )[0]
        
        # Generate random timestamp
        time_delta = random.random() * (end_date - start_date).total_seconds()
        timestamp = start_date + timedelta(seconds=time_delta)
        
        # Calculate revenue
        revenue = round(product["price"] * quantity, 2)
        
        transaction = {
            "transaction_id": f"TXN{i+1:06d}",
            "product_id": product["product_id"],
            "product_name": product["name"],
            "category": product["category"],
            "quantity": quantity,
            "unit_price": product["price"],
            "revenue": revenue,
            "timestamp": timestamp.isoformat()
        }
        sales.append(transaction)
    
    # Sort by timestamp
    sales.sort(key=lambda x: x["timestamp"])
    
    return sales
