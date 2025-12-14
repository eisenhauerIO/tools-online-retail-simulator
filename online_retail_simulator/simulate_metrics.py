"""
Interface for simulating product metrics.
Dispatches to rule-based implementation based on method argument.
"""
import pandas as pd
from typing import Optional

from typing import Dict, Optional
import pandas as pd

def simulate_metrics(product_characteristics: pd.DataFrame, config_path: str, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Simulate product metrics using the backend specified in config.
    Args:
        product_characteristics: DataFrame of product characteristics
        config_path: Path to JSON configuration file
        config: Optional pre-loaded config (avoids re-reading)
    Returns:
        DataFrame of product metrics
    """
    from .config_processor import process_config
    config_loaded = process_config(config_path) if config is None else config
    simulator_mode = config_loaded["SIMULATOR"]["mode"]
    # Use simulator_mode to select backend
    if simulator_mode == "rule":
        from .simulate_metrics_rule_based import simulate_metrics_rule_based
        return simulate_metrics_rule_based(product_characteristics, config_path)
    elif simulator_mode == "synthesizer":
        from .simulate_metrics_synthesizer_based import simulate_metrics_synthesizer_based
        return simulate_metrics_synthesizer_based(product_characteristics, config_path)
    else:
        raise ValueError(f"Unknown metrics simulator mode: {simulator_mode}")
