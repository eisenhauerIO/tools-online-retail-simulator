"""
Example demonstrating synthesizer-based simulation using Gaussian Copula.

This script shows:
1. Loading training data from CSV
2. Training a Gaussian Copula synthesizer
3. Generating synthetic product characteristics
"""

from online_retail_simulator import simulate_characteristics


def main():
    print("\n" + "=" * 60)
    print("SYNTHESIZER SIMULATION DEMO")
    print("=" * 60)
    print("Using Gaussian Copula synthesizer with training data\n")

    try:
        # Generate synthetic characteristics using synthesizer
        print("Step 1: Loading training data and training synthesizer...")
        products_df = simulate_characteristics("config_synthesizer_simulation.yaml")

        print(f"✓ Generated {len(products_df)} synthetic products")
        print(f"✓ Columns: {list(products_df.columns)}")

        # Show category breakdown
        print(f"\nCategory breakdown:")
        if 'category' in products_df.columns:
            category_counts = products_df['category'].value_counts()
            for category, count in category_counts.items():
                print(f"  {category}: {count} products")

        # Show price statistics
        if 'price' in products_df.columns:
            print(f"\nPrice statistics:")
            print(f"  Min price: ${products_df['price'].min():.2f}")
            print(f"  Max price: ${products_df['price'].max():.2f}")
            print(f"  Mean price: ${products_df['price'].mean():.2f}")

        print("\n" + "=" * 60)
        print("Synthesizer simulation complete!")
        print("=" * 60)
        print("This demonstrates ML-based synthetic data generation")
        print("using Gaussian Copula from the SDV library.\n")

    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Install SDV with: pip install online-retail-simulator[synthesizer]")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
