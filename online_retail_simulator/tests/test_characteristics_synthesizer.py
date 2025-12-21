import os

import pandas as pd
import pytest

from online_retail_simulator import JobInfo
from online_retail_simulator.simulate import simulate_characteristics

from .import_helpers import has_synthesizer

pytestmark = pytest.mark.skipif(not has_synthesizer(), reason="SDV dependencies not installed")


def test_characteristics_synthesizer():
    config_path = os.path.join(os.path.dirname(__file__), "config_synthesizer.yaml")
    job_info = simulate_characteristics(config_path)

    assert isinstance(job_info, JobInfo)

    df = job_info.load_df("products")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "product_id" in df.columns
    assert "price" in df.columns
    assert "category" in df.columns
