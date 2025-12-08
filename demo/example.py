"""
Example script demonstrating the online-retail-simulator package.

This script shows two use cases:
1. Basic retail data generation
2. Catalog enrichment for causal inference
"""

from online_retail_simulator import simulate


def main():
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Retail Data Generation")
    print("=" * 70)
    print("Generating synthetic product catalog and sales transactions")
    print("without enrichment treatment.\n")
    
    simulate("demo/config_basic.json")
    
    print("\n\n" + "=" * 70)
    print("EXAMPLE 2: Catalog Enrichment for Causal Inference")
    print("=" * 70)
    print("This example demonstrates causal inference teaching scenario.")
    print("- Enrichment: 50% quantity boost applied to 50% of products")
    print("- Start date: 2024-11-15 (midpoint of simulation)")
    print("- Outputs: Baseline, Factual, and Counterfactual sales data\n")
    
    simulate("demo/config_enrichment.json")
    
    print("\n" + "=" * 70)
    print("Analysis Guide: Measuring Causal Impact")
    print("=" * 70)
    print("""
The enrichment simulation generates three key datasets:

1. products_enriched.json
   - Contains treatment assignment (enriched: true/false)
   - Use to identify treated vs. control products

2. sales_counterfactual.json
   - Baseline sales without any treatment effect
   - Represents "what would have happened" without enrichment

3. sales_factual.json
   - Sales with treatment effect applied to enriched products
   - Represents observed reality with enrichment

Causal Inference Approaches:

A. Simple Difference
   Compare total revenue: factual - counterfactual = treatment effect

B. Difference-in-Differences (DiD)
   Compare enriched vs. non-enriched products before vs. after 2024-11-15
   Accounts for time trends and product-specific patterns

C. Synthetic Control
   Use non-enriched products to create counterfactual for enriched products
   More robust to heterogeneous treatment effects

Key Files Location: demo/output/
    """)
    
    print("✓ Examples complete! Check demo/output/ for all generated files.\n")


if __name__ == "__main__":
    main()
