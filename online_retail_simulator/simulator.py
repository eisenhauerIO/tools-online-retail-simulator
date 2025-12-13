"""Main simulator interface for generating and exporting retail data."""

from typing import Tuple

import pandas as pd

from .simulator_rule_based import simulate_rule_based


def simulate(config_path: str, mode: str | None = None, **kwargs) -> pd.DataFrame:
    """
    Unified simulation entrypoint driven by SIMULATOR.mode in config.

    Args:
        config_path: Path to JSON configuration file
        df: (optional) DataFrame for synthesizer mode
        synthesizer_type: (optional) SDV synthesizer type

    Returns:
        Single DataFrame (merged sales/products for rule mode, synthetic for synthesizer mode)
    """
    from .config_processor import process_config

    config = process_config(config_path)
    sim_mode = config.get("SIMULATOR", {}).get("mode", "rule")

    if sim_mode == "rule":
        return simulate_rule_based(config_path, config=config)
    if sim_mode == "synthesizer":
        from .simulator_synthesizer_based import simulate_synthesizer_based
        df = kwargs.get("df")
        synthesizer_type = kwargs.get("synthesizer_type", "gaussian_copula")
        if df is None:
            raise ValueError("df must be provided for synthesizer mode")
        return simulate_synthesizer_based(df=df, num_rows=len(df), synthesizer_type=synthesizer_type)
    raise ValueError("mode must be 'rule' or 'synthesizer'")
