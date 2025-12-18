"""
Example demonstrating default simulation using built-in rule-based generation.

This script shows:
1. Basic product catalog generation across multiple categories
2. Daily sales transaction simulation
3. Built-in rule-based approach with configurable parameters
"""

from online_retail_simulator import simulate, simulate_characteristics


df = simulate_characteristics("config_default_simulation.yaml")
print(df)
