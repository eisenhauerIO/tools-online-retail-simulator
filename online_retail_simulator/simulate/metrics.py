"""
Interface for simulating product metrics.
Dispatches to rule-based implementation based on method argument.
"""

from typing import Dict, Optional

import pandas as pd


def simulate_metrics(
    product_characteristics: pd.DataFrame,
    config_path: str,
    config: Optional[Dict] = None,
) -> pd.DataFrame:
    """
    Simulate product metrics using the backend specified in config.
    Args:
        product_characteristics: DataFrame of product characteristics
        config_path: Path to JSON configuration file
        config: Optional pre-loaded config (avoids re-reading)
    Returns:
        DataFrame of product metrics
    """
    from ..config_processor import process_config

    config_loaded = process_config(config_path)

    # Check for mode configuration - exactly one must be present
    if "RULE" in config_loaded:
        # Check if a custom rule function is specified
        rule_config = config_loaded["RULE"]
        metrics_config = rule_config.get("METRICS", {})
        custom_function = metrics_config.get("FUNCTION", "default")

        # Merge PARAMS into rule_config for backward compatibility
        if "PARAMS" in metrics_config:
            # Convert lowercase params to uppercase for backward compatibility
            params = {k.upper(): v for k, v in metrics_config["PARAMS"].items()}
            rule_config.update(params)

        from .rule_registry import SimulationRegistry

        func = SimulationRegistry.get_metrics_function(custom_function)
        return func(product_characteristics, config_path, config=config_loaded)

    elif "SYNTHESIZER" in config_loaded:
        from .metrics_synthesizer_based import simulate_metrics_synthesizer_based

        return simulate_metrics_synthesizer_based(product_characteristics, config_path)

    else:
        raise ValueError("Config must contain either RULE or SYNTHESIZER block")
