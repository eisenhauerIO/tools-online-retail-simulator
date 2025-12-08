"""Generate synthetic product data."""

import random
from typing import List, Dict


CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Books",
    "Sports & Outdoors",
    "Toys & Games",
    "Food & Beverage",
    "Health & Beauty"
]

PRODUCT_NAMES = {
    "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "Monitor", "Keyboard", "Mouse", "Webcam"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sweater", "Dress", "Shorts", "Hoodie", "Socks"],
    "Home & Garden": ["Chair", "Table", "Lamp", "Rug", "Curtains", "Vase", "Mirror", "Clock"],
    "Books": ["Novel", "Textbook", "Cookbook", "Biography", "Comic", "Magazine", "Journal", "Guide"],
    "Sports & Outdoors": ["Ball", "Bike", "Tent", "Backpack", "Yoga Mat", "Weights", "Running Shoes", "Water Bottle"],
    "Toys & Games": ["Board Game", "Puzzle", "Action Figure", "Doll", "Building Blocks", "Card Game", "Stuffed Animal", "Remote Car"],
    "Food & Beverage": ["Coffee", "Tea", "Snacks", "Chocolate", "Juice", "Cookies", "Nuts", "Energy Bar"],
    "Health & Beauty": ["Shampoo", "Lotion", "Soap", "Toothpaste", "Perfume", "Makeup", "Vitamins", "Sunscreen"]
}

PRICE_RANGES = {
    "Electronics": (50, 1500),
    "Clothing": (15, 200),
    "Home & Garden": (20, 500),
    "Books": (10, 60),
    "Sports & Outdoors": (15, 300),
    "Toys & Games": (10, 100),
    "Food & Beverage": (5, 50),
    "Health & Beauty": (8, 80)
}


def generate_product_data(n_products: int = 100, seed: int = None) -> List[Dict]:
    """
    Generate synthetic product data.
    
    Args:
        n_products: Number of products to generate (default: 100)
        seed: Random seed for reproducibility (default: None)
    
    Returns:
        List of product dictionaries with id, name, category, and price
    """
    if seed is not None:
        random.seed(seed)
    
    products = []
    
    for i in range(n_products):
        category = random.choice(CATEGORIES)
        product_name = random.choice(PRODUCT_NAMES[category])
        price_min, price_max = PRICE_RANGES[category]
        price = round(random.uniform(price_min, price_max), 2)
        
        product = {
            "product_id": f"PROD{i+1:04d}",
            "name": product_name,
            "category": category,
            "price": price
        }
        products.append(product)
    
    return products
