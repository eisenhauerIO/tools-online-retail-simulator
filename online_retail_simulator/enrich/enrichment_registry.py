"""
Impact-based enrichment registry for custom user-defined enrichment functions.

This module provides a registration system that allows users to register their own
impact-based enrichment functions. The default impact functions are automatically registered.
"""

import importlib
import inspect
from typing import Any, Callable, Dict, List

# Global registry for enrichment functions
_ENRICHMENT_REGISTRY: Dict[str, Callable] = {}

# Flag to track if defaults have been registered
_DEFAULTS_REGISTERED = False


def _register_default_functions():
    """Register the default impact-based enrichment functions."""
    global _DEFAULTS_REGISTERED
    if _DEFAULTS_REGISTERED:
        return

    from .enrichment_library import combined_boost, probability_boost, quantity_boost

    _ENRICHMENT_REGISTRY["quantity_boost"] = quantity_boost
    _ENRICHMENT_REGISTRY["probability_boost"] = probability_boost
    _ENRICHMENT_REGISTRY["combined_boost"] = combined_boost
    _DEFAULTS_REGISTERED = True


class EnrichmentRegistry:
    """Registry for managing custom enrichment functions."""

    @staticmethod
    def register_enrichment_function(name: str, func: Callable) -> None:
        """
        Register an enrichment function by name.

        Args:
            name: Name to register the function under
            func: Function that takes (sales: list, **kwargs) -> list

        Raises:
            ValueError: If function signature is invalid
        """
        # Validate function signature
        sig = inspect.signature(func)
        if "sales" not in sig.parameters:
            raise ValueError(f"Function {func.__name__} must have 'sales' parameter")

        # Store in registry
        _ENRICHMENT_REGISTRY[name] = func

    @staticmethod
    def register_module(module_name: str) -> None:
        """
        Register all functions from a module that match enrichment signature.

        Args:
            module_name: Name of module to import and register functions from

        Raises:
            ImportError: If module cannot be imported
        """
        # Try to import from online_retail_simulator package first
        try:
            module = importlib.import_module(f"online_retail_simulator.{module_name}")
        except (ImportError, ModuleNotFoundError):
            # Fall back to importing as standalone module
            module = importlib.import_module(module_name)

        # Register all functions that have the right signature
        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj) and not name.startswith("_"):
                try:
                    sig = inspect.signature(obj)
                    if "sales" in sig.parameters:
                        _ENRICHMENT_REGISTRY[name] = obj
                except (ValueError, TypeError):
                    # Skip objects that don't have valid signatures
                    continue

    @staticmethod
    def get_enrichment_function(name: str) -> Callable:
        """
        Get a registered enrichment function by name.

        Args:
            name: Name of the registered function

        Returns:
            The registered function

        Raises:
            KeyError: If function is not registered
        """
        _register_default_functions()
        if name not in _ENRICHMENT_REGISTRY:
            available = list(_ENRICHMENT_REGISTRY.keys())
            raise KeyError(f"Enrichment function '{name}' not registered. " f"Available: {available}")
        return _ENRICHMENT_REGISTRY[name]

    @staticmethod
    def list_enrichment_functions() -> List[str]:
        """List all registered enrichment function names."""
        _register_default_functions()
        return list(_ENRICHMENT_REGISTRY.keys())

    @staticmethod
    def clear_registry() -> None:
        """Clear all registered enrichment functions (useful for testing)."""
        global _DEFAULTS_REGISTERED
        _ENRICHMENT_REGISTRY.clear()
        _DEFAULTS_REGISTERED = False


# Convenience functions for direct access
def register_enrichment_function(name: str, func: Callable) -> None:
    """Register an enrichment function."""
    EnrichmentRegistry.register_enrichment_function(name, func)


def register_enrichment_module(module_name: str) -> None:
    """Register all compatible functions from a module."""
    EnrichmentRegistry.register_module(module_name)


def list_enrichment_functions() -> List[str]:
    """List all registered enrichment functions."""
    return EnrichmentRegistry.list_enrichment_functions()


def clear_enrichment_registry() -> None:
    """Clear all registered enrichment functions."""
    EnrichmentRegistry.clear_registry()


def load_effect_function(module_name: str, function_name: str) -> Callable:
    """
    Load treatment effect function from registry.

    Args:
        module_name: Name of module (ignored, kept for backward compatibility)
        function_name: Name of function in registry

    Returns:
        Treatment effect function
    """
    return EnrichmentRegistry.get_enrichment_function(function_name)
