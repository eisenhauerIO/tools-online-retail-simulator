"""
Simulate workflow: combines characteristics and metrics simulation.
"""

from .characteristics import simulate_characteristics
from .metrics import simulate_metrics


def simulate(config_path):
    """
    Runs simulate_characteristics and simulate_metrics in sequence.

    Args:
        config_path: Path to configuration file

    Returns:
        DataFrame with simulation results (metrics)
    """
    from ..config_processor import process_config
    from ..storage import save_simulation_data

    config = process_config(config_path)

    # Generate data
    products = simulate_characteristics(config_path)
    sales = simulate_metrics(products, config_path)

    # Save if STORAGE configured
    if "STORAGE" in config:
        save_simulation_data(products, sales, config["STORAGE"]["PATH"], config, config_path)

    return sales
