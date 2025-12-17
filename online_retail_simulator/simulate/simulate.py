"""
Simulate workflow: combines characteristics and metrics simulation.
"""

from .characteristics import simulate_characteristics
from .metrics import simulate_metrics


def simulate(config_path):
    """
    Runs simulate_characteristics and simulate_metrics in sequence.
    Returns the result from simulate_metrics.
    """
    products = simulate_characteristics(config_path)
    return simulate_metrics(products, config_path)
