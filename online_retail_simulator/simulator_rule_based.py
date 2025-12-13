"""Rule-based product and sales generators combined in one module."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import pandas as pd


def simulate_rule_based(config_path: str, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Main entry point: run rule-based simulation from JSON configuration file.

    Returns a single merged DataFrame (sales joined with products on 'product_id').

    Args:
        config_path: Path to JSON configuration file
        config: Optional pre-loaded config (avoids re-reading)

    Returns:
        Merged DataFrame (sales joined with products)
    """
    # Lazy import to avoid circular dependencies
    from .enrichment_application import assign_enrichment, load_effect_function, apply_enrichment_to_sales, parse_effect_spec
    from .config_processor import process_config
    
    if config is None:
        config = process_config(config_path)

    rule_config = config["RULE"]
    seed = config.get("SEED", 42)
    output_dir = config.get("OUTPUT", {}).get("dir", "output")
    file_prefix = config.get("OUTPUT", {}).get("file_prefix", "run")

    num_products = rule_config.get("NUM_PRODUCTS", 100)
    date_start = rule_config.get("DATE_START")
    date_end = rule_config.get("DATE_END")
    sale_prob = rule_config.get("SALE_PROB", 0.7)

    # Only enable enrichment if configured under RULE
    rule_section = config.get("RULE", {})
    enrichment_config = rule_section.get("ENRICHMENT")
    has_enrichment = enrichment_config is not None and enrichment_config.get("START_DATE")
    
    print("=" * 60)
    print("Online Retail Simulator")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Seed:         {seed}")
    print(f"  Products:     {num_products}")
    print(f"  Date Range:   {date_start} to {date_end}")
    print(f"  Output Dir:   {output_dir}")
    if has_enrichment:
        print(f"  Mode:         Baseline + Enrichment")
    
    # Generate baseline products
    print(f"\nGenerating {num_products} products...")
    products = generate_product_data(n_products=num_products, seed=seed)
    print(f"✓ Generated {len(products)} products")

    # Generate baseline sales
    print(f"\nGenerating baseline sales records (all product-date combinations)...")
    sales = generate_sales_data(
        products=products,
        date_start=date_start,
        date_end=date_end,
        seed=seed,
        sale_probability=sale_prob
    )
    print(f"\u2713 Generated {len(sales)} baseline records (product-date pairs)")
    products_file = rule_config.get("PRODUCTS_FILE", f"{file_prefix}_products.json")
    sales_file = rule_config.get("SALES_FILE", f"{file_prefix}_sales.json")
    products_path = f"{output_dir}/{products_file}"
    sales_path = f"{output_dir}/{sales_file}"
    _save_to_json(products, products_path)
    _save_to_json(sales, sales_path)
    
    # Apply enrichment if configured
    if has_enrichment:
        enrichment_start = enrichment_config.get("START_DATE")
        enrichment_fraction = enrichment_config.get("FRACTION", 0.5)
        effect_spec = enrichment_config.get("EFFECT", "quantity_boost:0.5")
        
        enriched_products_file = enrichment_config.get("PRODUCTS_FILE", f"{file_prefix}_enriched.json")
        factual_sales_file = enrichment_config.get("SALES_FACTUAL_FILE", f"{file_prefix}_factual.json")
        counterfactual_sales_file = enrichment_config.get("SALES_COUNTERFACTUAL_FILE", f"{file_prefix}_counterfactual.json")
        
        if not enrichment_start:
            raise ValueError("ENRICHMENT configuration must include START_DATE")
        
        # Parse EFFECT specification
        effect_module, effect_function_name, effect_params = parse_effect_spec(effect_spec)
        
        print(f"\n" + "=" * 60)
        print("Applying Enrichment Treatment")
        print("=" * 60)
        print(f"  Start Date:   {enrichment_start}")
        print(f"  Fraction:     {enrichment_fraction:.0%}")
        print(f"  Effect:       {effect_module}.{effect_function_name}")
        print(f"  Params:       {effect_params}")
        
        # Assign enrichment treatment
        print(f"\nAssigning enrichment to {enrichment_fraction:.0%} of products...")
        enriched_products = assign_enrichment(products, enrichment_fraction, seed)
        n_enriched = sum(1 for p in enriched_products if p.get('enriched', False))
        print(f"✓ Assigned enrichment to {n_enriched} products")
        
        # Load effect function
        print(f"\nLoading treatment effect function...")
        effect_function = load_effect_function(effect_module, effect_function_name)
        print(f"✓ Loaded {effect_function_name} from {effect_module}")

        # Merge sales with product info for enrichment
        sales_df = pd.DataFrame(sales)
        products_df = pd.DataFrame(products)[['product_id', 'price']]
        merged_sales = sales_df.merge(products_df, on='product_id', how='left')
        merged_sales = merged_sales.rename(columns={'price': 'unit_price'})
        sales_for_enrichment = merged_sales.to_dict(orient='records')

        # Apply enrichment to create factual sales
        print(f"\nApplying treatment effect to create factual sales...")
        factual_sales = apply_enrichment_to_sales(
            sales_for_enrichment,
            enriched_products,
            enrichment_start,
            effect_function,
            **effect_params
        )
        # Extract only minimal fields for output
        factual_sales = [
            {k: sale[k] for k in ('product_id', 'date', 'quantity', 'revenue')}
            for sale in factual_sales
        ]
        print(f"✓ Created factual sales with {len(factual_sales)} transactions")
        
        # Counterfactual = baseline (no treatment)
        counterfactual_sales = sales
        
        # Save enrichment outputs
        print(f"\nSaving enrichment data to {output_dir}/...")
        enriched_products_path = f"{output_dir}/{enriched_products_file}"
        factual_sales_path = f"{output_dir}/{factual_sales_file}"
        counterfactual_sales_path = f"{output_dir}/{counterfactual_sales_file}"
        
        _save_to_json(enriched_products, enriched_products_path)
        _save_to_json(factual_sales, factual_sales_path)
        _save_to_json(counterfactual_sales, counterfactual_sales_path)
        
        # Display enrichment summary
        print(f"\n" + "=" * 60)
        print("Enrichment Summary")
        print("=" * 60)
        
        factual_revenue = sum(sale["revenue"] for sale in factual_sales)
        counterfactual_revenue = sum(sale["revenue"] for sale in counterfactual_sales)
        revenue_lift = ((factual_revenue - counterfactual_revenue) / counterfactual_revenue) * 100
        
        print(f"Enriched Products:  {n_enriched} of {len(products)} ({enrichment_fraction:.0%})")
        print(f"Counterfactual Revenue: ${counterfactual_revenue:,.2f}")
        print(f"Factual Revenue:        ${factual_revenue:,.2f}")
        print(f"Revenue Lift:           {revenue_lift:.2f}%")
    
    # Display final summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    total_revenue = sum(sale["revenue"] for sale in sales)
    total_quantity = sum(sale["quantity"] for sale in sales)
    categories = set(product["category"] for product in products)
    unique_dates = len(set(sale["date"] for sale in sales))
    
    print(f"Total Products:     {len(products)}")
    print(f"Product Categories: {len(categories)}")
    print(f"Total Products:     {len(products)}")
    print(f"Total Records:      {len(sales)} (product-date pairs)")
    print(f"Days Simulated:     {unique_dates}")
    print(f"Total Units Sold:   {total_quantity}")
    print(f"Total Revenue:      ${total_revenue:,.2f}")
    
    print(f"\n\u2713 Simulation complete!")
    
    # Convert to DataFrames and return
    products_df = pd.DataFrame(products)
    sales_df = pd.DataFrame(sales)
    merged_df = sales_df.merge(products_df, on="product_id", how="left")
    return merged_df


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
    
    products: List[Dict] = []
    for i in range(n_products):
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
    return products


def generate_sales_data(
    products: List[Dict],
    date_start: str,
    date_end: str,
    seed: Optional[int] = None,
    sale_probability: float = 0.7
) -> List[Dict]:
    """
    Generate synthetic daily sales transactions from product data.
    
    Generates a row for every product-date combination. Each product-day
    has a probability of generating a sale (default 70%). If no sale occurs,
    a row is still present with quantity and revenue set to 0.

    Args:
        products: List of product dictionaries
        date_start: Start date in "YYYY-MM-DD" format
        date_end: End date in "YYYY-MM-DD" format
        seed: Random seed for reproducibility (default: None)
        sale_probability: Probability of a sale for each product-day (default: 0.7)

    Returns:
        List of sales transaction dictionaries with fields: product_id, date, quantity, revenue
    """
    if seed is not None:
        random.seed(seed)

    start_date = datetime.strptime(date_start, "%Y-%m-%d")
    end_date = datetime.strptime(date_end, "%Y-%m-%d")

    sales: List[Dict] = []
    current_date = start_date
    while current_date <= end_date:
        for product in products:
            sale_occurred = random.random() < sale_probability
            if sale_occurred:
                quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
                revenue = round(product["price"] * quantity, 2)
            else:
                quantity = 0
                revenue = 0.0
            sales.append({
                "product_id": product["product_id"],
                "date": current_date.strftime("%Y-%m-%d"),
                "quantity": quantity,
                "revenue": revenue
            })
        current_date += timedelta(days=1)

    return sales


# ============================================================================
# Private Section: Constants and Helpers
# ============================================================================

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


def _save_to_json(data: List[Dict], filepath: str, indent: int = 2) -> None:
    """Save data to JSON file."""
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=indent)
    print(f"Data saved to {filepath}")
