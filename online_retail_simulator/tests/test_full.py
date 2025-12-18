"""
Test for the full simulation workflow using config_rule.yaml.
"""

import os

import pandas as pd

from online_retail_simulator.simulate import simulate


def test_simulate_full_rule():
    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    job_id = simulate(config_path)
    assert isinstance(job_id, str)
    assert job_id.startswith("job-")

    # Load results to verify they exist
    from online_retail_simulator import load_job_results

    products_df, sales_df = load_job_results(job_id)
    assert isinstance(products_df, pd.DataFrame)
    assert isinstance(sales_df, pd.DataFrame)
    assert not products_df.empty
    assert not sales_df.empty
