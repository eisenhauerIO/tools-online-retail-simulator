"""
Impact-based enrichment registry for custom user-defined enrichment functions.

This module provides a registration system that allows users to register their own
impact-based enrichment functions.
"""

from typing import Callable, List

from online_retail_simulator.core import FunctionRegistry


def _load_enrichment_defaults(registry: FunctionRegistry) -> None:
    """Load default enrichment functions."""
    from .enrichment_library import combined_boost, probability_boost, quantity_boost

    registry.register("quantity_boost", quantity_boost)
    registry.register("probability_boost", probability_boost)
    registry.register("combined_boost", combined_boost)


# Registry instance
_enrichment_registry = FunctionRegistry(
    name="enrichment",
    required_params={"sales"},
    default_loader=_load_enrichment_defaults,
)


# Public API functions
def register_enrichment_function(name: str, func: Callable) -> None:
    """Register an enrichment function."""
    _enrichment_registry.register(name, func)


def register_enrichment_module(module_name: str) -> None:
    """Register all compatible functions from a module."""
    _enrichment_registry.register_from_module(module_name)


def list_enrichment_functions() -> List[str]:
    """List all registered enrichment functions."""
    return _enrichment_registry.list()


def clear_enrichment_registry() -> None:
    """Clear all registered enrichment functions."""
    _enrichment_registry.clear()


def load_effect_function(module_name: str, function_name: str) -> Callable:
    """
    Load treatment effect function from registry.

    Args:
        module_name: Name of module (ignored, kept for backward compatibility)
        function_name: Name of function in registry

    Returns:
        Treatment effect function
    """
    return _enrichment_registry.get(function_name)
