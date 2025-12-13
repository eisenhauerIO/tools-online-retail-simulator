import json
from pathlib import Path
from online_retail_simulator.simulator import simulate
from online_retail_simulator.simulator_synthesizer_based import simulate_synthesizer_based


# Use separate configs for rule and synthesizer steps
rule_config_path = str(Path(__file__).parent.parent / "demo" / "config_rule.json")
synth_config_path = str(Path(__file__).parent.parent / "demo" / "config_synthesizer.json")

# Step 1: Run rule-based simulation to get merged DataFrame
merged_df = simulate(rule_config_path, mode="rule")
print(f"Rule-based simulation: {merged_df.shape}")

# Step 2: Generate synthetic data from merged DataFrame
synthetic_df = simulate(synth_config_path, mode="synthesizer", df=merged_df, num_rows=len(merged_df))
print(f"Synthetic DataFrame: {synthetic_df.shape}")

# Optionally, save synthetic data to a file
output_path = Path(__file__).parent / "synthetic_merged.json"
synthetic_df.to_json(output_path, orient="records", indent=2)
print(f"Synthetic data saved to {output_path}")
