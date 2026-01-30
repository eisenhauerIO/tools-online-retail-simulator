"""
Rule-based simulation registry for custom user-defined simulation functions.

This module provides a registration system that allows users to register their own
rule-based simulation functions for both products and sales metrics.
"""

from typing import Callable, Dict, List

from online_retail_simulator.core import FunctionRegistry


def _load_products_defaults(registry: FunctionRegistry) -> None:
    """Load default products functions."""
    from .products_rule_based import simulate_products_rule_based

    registry.register("simulate_products_rule_based", simulate_products_rule_based)


def _load_metrics_defaults(registry: FunctionRegistry) -> None:
    """Load default metrics functions."""
    from .metrics_rule_based import simulate_metrics_rule_based

    registry.register("simulate_metrics_rule_based", simulate_metrics_rule_based)


# Registry instances
_products_registry = FunctionRegistry(
    name="products",
    required_params={"config"},
    default_loader=_load_products_defaults,
)

_metrics_registry = FunctionRegistry(
    name="metrics",
    required_params={"products", "config"},
    default_loader=_load_metrics_defaults,
)


# Public API functions
def register_products_function(name: str, func: Callable) -> None:
    """Register a products generation function."""
    _products_registry.register(name, func)


def register_metrics_function(name: str, func: Callable) -> None:
    """Register a metrics generation function."""
    _metrics_registry.register(name, func)


def register_simulation_module(module_name: str, prefix: str = "") -> None:
    """
    Register all compatible functions from a module.

    Functions are automatically detected based on their signatures:
    - Products functions: must have 'config' parameter
    - Metrics functions: must have 'products' and 'config' parameters
    """
    # Register products functions
    _products_registry.register_from_module(
        module_name,
        prefix,
        signature_filter=lambda params: "config" in params and "products" not in params,
    )

    # Register metrics functions
    _metrics_registry.register_from_module(
        module_name,
        prefix,
        signature_filter=lambda params: "products" in params and "config" in params,
    )


def get_simulation_function(func_type: str, name: str) -> Callable:
    """
    Get a registered simulation function.

    Args:
        func_type: Type of function ('products' or 'metrics')
        name: Name of the function

    Returns:
        The registered function
    """
    if func_type == "products":
        return _products_registry.get(name)
    elif func_type == "metrics":
        return _metrics_registry.get(name)
    else:
        raise ValueError(f"Invalid function type: {func_type}. Must be 'products' or 'metrics'")


def list_simulation_functions() -> Dict[str, List[str]]:
    """List all registered simulation functions."""
    return {
        "products": _products_registry.list(),
        "metrics": _metrics_registry.list(),
    }


def clear_simulation_registry() -> None:
    """Clear all registered simulation functions (useful for testing)."""
    _products_registry.clear()
    _metrics_registry.clear()
