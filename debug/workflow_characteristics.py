"""
Workflow script to simulate product characteristics and save output.
Reuses existing config structure and OUTPUT section for file path.
"""
from online_retail_simulator import simulate_characteristics



config_path = "debug/config_rule.json"
products = simulate_characteristics(config_path)

products.to_pickle("df_start.pkl")

config_path = "debug/config_synthesizer.json"
products = simulate_characteristics(config_path)

print(products)
