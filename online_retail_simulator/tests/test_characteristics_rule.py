import pytest
from online_retail_simulator.simulate_characteristics import simulate_characteristics
import pandas as pd

def test_characteristics_rule():
    import os
    config_path = os.path.join(os.path.dirname(__file__), "config_rule.json")
    df = simulate_characteristics(config_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "product_id" in df.columns
    assert "price" in df.columns
