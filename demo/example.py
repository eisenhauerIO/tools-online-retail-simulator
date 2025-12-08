"""
Example script demonstrating the online-retail-simulator package.

This script:
1. Generates synthetic product catalog data
2. Generates sales transactions from those products
3. Exports both datasets to JSON files
"""

from online_retail_simulator import generate_products, generate_sales, save_to_json


def main():
    # Set seed for reproducibility
    SEED = 42
    
    print("=" * 60)
    print("Online Retail Simulator - Demo")
    print("=" * 60)
    
    # Generate product catalog
    print("\n1. Generating product catalog...")
    products = generate_products(n_products=50, seed=SEED)
    print(f"   ✓ Generated {len(products)} products")
    print(f"   Example product: {products[0]}")
    
    # Generate sales transactions
    print("\n2. Generating sales transactions...")
    sales = generate_sales(
        products=products,
        n_transactions=200,
        days_back=30,
        seed=SEED
    )
    print(f"   ✓ Generated {len(sales)} transactions")
    print(f"   Example transaction: {sales[0]}")
    
    # Save to JSON files
    print("\n3. Saving data to JSON files...")
    save_to_json(products, "demo/output/products.json")
    save_to_json(sales, "demo/output/sales.json")
    
    # Display summary statistics
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)
    
    total_revenue = sum(sale["revenue"] for sale in sales)
    total_quantity = sum(sale["quantity"] for sale in sales)
    categories = set(product["category"] for product in products)
    
    print(f"Total Products:     {len(products)}")
    print(f"Product Categories: {len(categories)}")
    print(f"Total Transactions: {len(sales)}")
    print(f"Total Units Sold:   {total_quantity}")
    print(f"Total Revenue:      ${total_revenue:,.2f}")
    print(f"Average Order:      ${total_revenue/len(sales):.2f}")
    
    print("\n✓ Demo complete! Check demo/output/ for generated JSON files.")


if __name__ == "__main__":
    main()
