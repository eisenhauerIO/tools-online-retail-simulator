"""
Rule-based simulation registry for custom user-defined simulation functions.

This module provides a registration system that allows users to register their own
rule-based simulation functions for both product characteristics and sales metrics.
"""

from typing import Callable, Dict, List

from online_retail_simulator.core import FunctionRegistry


def _load_characteristics_defaults(registry: FunctionRegistry) -> None:
    """Load default characteristics functions."""
    from .characteristics_rule_based import simulate_characteristics_rule_based

    registry.register("simulate_characteristics_rule_based", simulate_characteristics_rule_based)


def _load_metrics_defaults(registry: FunctionRegistry) -> None:
    """Load default metrics functions."""
    from .metrics_rule_based import simulate_metrics_rule_based

    registry.register("simulate_metrics_rule_based", simulate_metrics_rule_based)


# Registry instances
_characteristics_registry = FunctionRegistry(
    name="characteristics",
    required_params={"config"},
    default_loader=_load_characteristics_defaults,
)

_metrics_registry = FunctionRegistry(
    name="metrics",
    required_params={"product_characteristics", "config"},
    default_loader=_load_metrics_defaults,
)


# Public API functions
def register_characteristics_function(name: str, func: Callable) -> None:
    """Register a characteristics generation function."""
    _characteristics_registry.register(name, func)


def register_metrics_function(name: str, func: Callable) -> None:
    """Register a metrics generation function."""
    _metrics_registry.register(name, func)


def register_simulation_module(module_name: str, prefix: str = "") -> None:
    """
    Register all compatible functions from a module.

    Functions are automatically detected based on their signatures:
    - Characteristics functions: must have 'config' parameter
    - Metrics functions: must have 'product_characteristics' and 'config_path' parameters
    """
    # Register characteristics functions
    _characteristics_registry.register_from_module(
        module_name,
        prefix,
        signature_filter=lambda params: "config" in params and "product_characteristics" not in params,
    )

    # Register metrics functions
    _metrics_registry.register_from_module(
        module_name,
        prefix,
        signature_filter=lambda params: "product_characteristics" in params and "config_path" in params,
    )


def get_simulation_function(func_type: str, name: str) -> Callable:
    """
    Get a registered simulation function.

    Args:
        func_type: Type of function ('characteristics' or 'metrics')
        name: Name of the function

    Returns:
        The registered function
    """
    if func_type == "characteristics":
        return _characteristics_registry.get(name)
    elif func_type == "metrics":
        return _metrics_registry.get(name)
    else:
        raise ValueError(f"Invalid function type: {func_type}. Must be 'characteristics' or 'metrics'")


def list_simulation_functions() -> Dict[str, List[str]]:
    """List all registered simulation functions."""
    return {
        "characteristics": _characteristics_registry.list(),
        "metrics": _metrics_registry.list(),
    }


def clear_simulation_registry() -> None:
    """Clear all registered simulation functions (useful for testing)."""
    _characteristics_registry.clear()
    _metrics_registry.clear()
