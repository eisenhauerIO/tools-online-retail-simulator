"""
Example script demonstrating the online-retail-simulator package.

This script shows two use cases:
1. Basic retail data generation (rule-based)
2. Synthesizer-based generation (SDV)
"""

from online_retail_simulator import simulate


def main():
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Rule-Based Generation")
    print("=" * 70)
    print("Generating synthetic product catalog and sales transactions (baseline only).\n")
    simulate("demo/config_rule.json")

    print("\n\n" + "=" * 70)
    print("EXAMPLE 2: Synthesizer-Based Generation")
    print("=" * 70)
    print("Sampling synthetic products and sales from SDV-trained models.\n")
    simulate("demo/config_synthesizer.json")

    print("\n" + "=" * 70)
    print("Examples complete")
    print("=" * 70)
    print("Check demo/output and demo/output_mc for generated files.\n")


if __name__ == "__main__":
    main()
