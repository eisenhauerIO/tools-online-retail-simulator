"""
Enrich workflow: applies enrichment treatments to sales data.
"""

import pandas as pd

from .application import enrich as apply_enrichment


def enrich(config_path: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply enrichment to a DataFrame using a config file.

    Args:
        config_path: Path to enrichment config (YAML or JSON)
        df: DataFrame with sales data (must include asin)

    Returns:
        DataFrame with enrichment applied (factual version)
    """
    return apply_enrichment(config_path, df)
