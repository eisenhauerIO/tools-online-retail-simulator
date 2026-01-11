import os

import pandas as pd

from online_retail_simulator import JobInfo
from online_retail_simulator.simulate import simulate_characteristics


def test_characteristics_rule():
    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    job_info = simulate_characteristics(config_path)

    assert isinstance(job_info, JobInfo)

    df = job_info.load_df("products")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "product_identifier" in df.columns
    assert "price" in df.columns
