"""
Interface for simulating product characteristics.
Dispatches to rule-based or synthesizer-based implementation based on config.
"""

from typing import Dict, Optional

import pandas as pd


def simulate_characteristics(config_path: str, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Simulate product characteristics using the backend specified in config.
    Args:
        config_path: Path to JSON configuration file
        config: Optional pre-loaded config (avoids re-reading)
    Returns:
        List of product dictionaries
    """
    from .config_processor import process_config

    config_loaded = process_config(config_path)
    simulator_mode = config_loaded["SIMULATOR"]["mode"]
    # Use simulator_mode to select backend
    if simulator_mode == "rule":
        from .simulate_characteristics_rule_based import simulate_characteristics_rule_based

        return simulate_characteristics_rule_based(config_path)
    elif simulator_mode == "synthesizer":
        from .simulate_characteristics_synthesizer_based import simulate_characteristics_synthesizer_based

        return simulate_characteristics_synthesizer_based(config_loaded)
    else:
        raise ValueError(f"Unknown simulator mode: {simulator_mode}")
