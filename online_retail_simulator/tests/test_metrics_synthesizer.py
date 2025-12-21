import os

import pandas as pd
import pytest

from online_retail_simulator import load_dataframe
from online_retail_simulator.simulate import simulate_characteristics, simulate_metrics

from .import_helpers import has_synthesizer

pytestmark = pytest.mark.skipif(not has_synthesizer(), reason="SDV dependencies not installed")


def test_metrics_synthesizer():
    config_path = os.path.join(os.path.dirname(__file__), "config_synthesizer.yaml")
    job_info = simulate_characteristics(config_path)
    job_info = simulate_metrics(job_info, config_path)

    df = load_dataframe(job_info, "sales")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "product_id" in df.columns
    assert "date" in df.columns
    assert "quantity" in df.columns
    assert "revenue" in df.columns
