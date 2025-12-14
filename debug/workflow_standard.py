"""
Workflow script to simulate product characteristics and save output.
Reuses existing config structure and OUTPUT section for file path.
"""
from online_retail_simulator import simulate_characteristics, simulate_metrics



for method in ["rule", "synthesizer"]:
    config_path = f"config_{method}.json"
    products = simulate_characteristics(config_path)    
    df_full = simulate_metrics(products, config_path)

    if method == 'rule':
        df_full.to_pickle("df_start.pkl")


