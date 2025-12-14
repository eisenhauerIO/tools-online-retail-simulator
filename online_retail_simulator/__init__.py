"""Online Retail Simulator - Generate synthetic retail data for experimentation."""

from .simulate import simulate
from .simulate_characteristics import simulate_characteristics
from .simulate_metrics import simulate_metrics

__version__ = "0.1.0"
__all__ = [
    "simulate",
    "simulate_characteristics",
    "simulate_metrics",
]
