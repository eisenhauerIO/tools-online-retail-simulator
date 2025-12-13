import pytest
from pathlib import Path
from online_retail_simulator.simulator import simulate

def test_e2e_workflow():
    rule_config = str(Path(__file__).parent / "config_rule.json")
    synth_config = str(Path(__file__).parent / "config_synthesizer.json")
    merged_df = simulate(rule_config)
    assert merged_df is not None
    assert not merged_df.empty
    synthetic_df = simulate(synth_config, df=merged_df)
    assert synthetic_df is not None
    assert not synthetic_df.empty
    assert synthetic_df.shape == merged_df.shape
