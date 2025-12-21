"""Generic function registry with signature validation and lazy default loading."""

import importlib
import inspect
from typing import Callable, Dict, List, Optional, Set


class FunctionRegistry:
    """Generic registry for callable functions with signature validation."""

    def __init__(
        self,
        name: str,
        required_params: Set[str],
        default_loader: Optional[Callable[["FunctionRegistry"], None]] = None,
    ):
        """
        Initialize a function registry.

        Args:
            name: Name of this registry (for error messages)
            required_params: Set of parameter names that registered functions must have
            default_loader: Optional callback to load default functions on first access
        """
        self._name = name
        self._required_params = required_params
        self._default_loader = default_loader
        self._registry: Dict[str, Callable] = {}
        self._defaults_loaded = False

    def _ensure_defaults_loaded(self) -> None:
        """Load default functions if not already loaded."""
        if not self._defaults_loaded and self._default_loader is not None:
            self._default_loader(self)
            self._defaults_loaded = True

    def register(self, name: str, func: Callable) -> None:
        """
        Register a function with signature validation.

        Args:
            name: Name to register the function under
            func: Function to register

        Raises:
            ValueError: If function signature doesn't include required parameters
        """
        sig = inspect.signature(func)
        params = set(sig.parameters.keys())

        if not self._required_params.issubset(params):
            raise ValueError(
                f"Function {func.__name__} must have parameters: {self._required_params}. " f"Found: {params}"
            )

        self._registry[name] = func

    def get(self, name: str) -> Callable:
        """
        Get a registered function by name.

        Args:
            name: Name of the function to retrieve

        Returns:
            The registered function

        Raises:
            KeyError: If function is not registered
        """
        self._ensure_defaults_loaded()

        if name not in self._registry:
            raise KeyError(
                f"{self._name.capitalize()} function '{name}' not registered. "
                f"Available: {list(self._registry.keys())}"
            )

        return self._registry[name]

    def list(self) -> List[str]:
        """List all registered function names."""
        self._ensure_defaults_loaded()
        return list(self._registry.keys())

    def clear(self) -> None:
        """Clear all registered functions (useful for testing)."""
        self._registry.clear()
        self._defaults_loaded = False

    def register_from_module(
        self,
        module_name: str,
        prefix: str = "",
        signature_filter: Optional[Callable[[Set[str]], bool]] = None,
    ) -> None:
        """
        Register all matching functions from a module.

        Args:
            module_name: Name of module to import and register functions from
            prefix: Optional prefix to add to function names when registering
            signature_filter: Optional function to check if a signature matches.
                              If None, uses required_params check.

        Raises:
            ImportError: If module cannot be imported
        """
        # Try to import from online_retail_simulator package first
        try:
            module = importlib.import_module(f"online_retail_simulator.{module_name}")
        except (ImportError, ModuleNotFoundError):
            # Fall back to importing as standalone module
            module = importlib.import_module(module_name)

        # Register all compatible functions
        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj) and not name.startswith("_"):
                try:
                    sig = inspect.signature(obj)
                    params = set(sig.parameters.keys())

                    # Check if function matches
                    if signature_filter is not None:
                        matches = signature_filter(params)
                    else:
                        matches = self._required_params.issubset(params)

                    if matches:
                        reg_name = f"{prefix}{name}" if prefix else name
                        self._registry[reg_name] = obj

                except (ValueError, TypeError):
                    # Skip objects that don't have valid signatures
                    continue
