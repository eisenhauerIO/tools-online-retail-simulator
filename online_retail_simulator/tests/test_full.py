"""
Test for the full simulation workflow using config_rule.yaml.
"""

import os

import pandas as pd

from online_retail_simulator import JobInfo, load_job_results
from online_retail_simulator.simulate import simulate


def test_simulate_full_rule():
    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    job_info = simulate(config_path)

    assert isinstance(job_info, JobInfo)
    assert job_info.job_id.startswith("job-")

    # Load results to verify they exist
    results = load_job_results(job_info)
    assert "products" in results
    assert "metrics" in results
    assert isinstance(results["products"], pd.DataFrame)
    assert isinstance(results["metrics"], pd.DataFrame)
    assert not results["products"].empty
    assert not results["metrics"].empty
