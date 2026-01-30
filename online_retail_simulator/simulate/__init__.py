"""Simulation module for generating synthetic retail data."""

from .metrics import simulate_metrics
from .product_details import simulate_product_details
from .products import simulate_products
from .rule_registry import (
    get_simulation_function,
    list_simulation_functions,
    register_metrics_function,
    register_products_function,
    register_simulation_module,
)
from .simulate import simulate

__all__ = [
    "simulate",
    "simulate_products",
    "simulate_product_details",
    "simulate_metrics",
    "register_products_function",
    "register_metrics_function",
    "register_simulation_module",
    "list_simulation_functions",
    "get_simulation_function",
]
