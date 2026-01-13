"""Tests for the unified FunctionRegistry."""

import pytest

from online_retail_simulator.core import FunctionRegistry


class TestFunctionRegistry:
    """Test cases for FunctionRegistry class."""

    def test_register_and_get(self):
        """Test basic registration and retrieval."""
        registry = FunctionRegistry("test", {"x"})

        def sample_func(x):
            return x * 2

        registry.register("double", sample_func)
        retrieved = registry.get("double")

        assert retrieved is sample_func
        assert retrieved(5) == 10

    def test_register_validates_signature(self):
        """Test that registration validates required parameters."""
        registry = FunctionRegistry("test", {"x", "y"})

        def valid_func(x, y):
            return x + y

        def invalid_func(a, b):
            return a + b

        # Valid function should register
        registry.register("valid", valid_func)
        assert "valid" in registry.list()

        # Invalid function should raise ValueError
        with pytest.raises(ValueError, match="must have parameters"):
            registry.register("invalid", invalid_func)

    def test_get_nonexistent_raises_keyerror(self):
        """Test that getting a non-existent function raises KeyError."""
        registry = FunctionRegistry("test", {"x"})

        with pytest.raises(KeyError, match="not registered"):
            registry.get("nonexistent")

    def test_list_functions(self):
        """Test listing registered functions."""
        registry = FunctionRegistry("test", {"x"})

        def func1(x):
            pass

        def func2(x):
            pass

        registry.register("func1", func1)
        registry.register("func2", func2)

        names = registry.list()
        assert "func1" in names
        assert "func2" in names
        assert len(names) == 2

    def test_clear_registry(self):
        """Test clearing the registry."""
        registry = FunctionRegistry("test", {"x"})

        def sample_func(x):
            pass

        registry.register("sample", sample_func)
        assert len(registry.list()) == 1

        registry.clear()
        assert len(registry.list()) == 0

    def test_lazy_default_loading(self):
        """Test that defaults are loaded lazily."""
        load_count = [0]

        def loader(reg):
            load_count[0] += 1

            def default_func(x):
                pass

            reg.register("default", default_func)

        registry = FunctionRegistry("test", {"x"}, default_loader=loader)

        # Defaults not loaded yet
        assert load_count[0] == 0

        # Accessing triggers load
        registry.list()
        assert load_count[0] == 1

        # Second access doesn't reload
        registry.list()
        assert load_count[0] == 1

    def test_clear_resets_defaults_loaded_flag(self):
        """Test that clear resets the defaults loaded flag."""
        load_count = [0]

        def loader(reg):
            load_count[0] += 1

            def default_func(x):
                pass

            reg.register("default", default_func)

        registry = FunctionRegistry("test", {"x"}, default_loader=loader)

        # First access loads defaults
        registry.list()
        assert load_count[0] == 1

        # Clear and access again reloads
        registry.clear()
        registry.list()
        assert load_count[0] == 2

    def test_extra_params_allowed(self):
        """Test that functions with extra parameters are allowed."""
        registry = FunctionRegistry("test", {"x"})

        def func_with_extras(x, y, z=None, **kwargs):
            return x

        registry.register("extras", func_with_extras)
        assert "extras" in registry.list()


class TestRegistryIntegration:
    """Integration tests with actual registries."""

    def test_simulation_registry_works(self):
        """Test that simulation registry functions work with new implementation."""
        from online_retail_simulator.simulate.rule_registry import (
            clear_simulation_registry,
            get_simulation_function,
            list_simulation_functions,
            register_characteristics_function,
        )

        clear_simulation_registry()

        def custom_characteristics(config):
            import pandas as pd

            return pd.DataFrame({"product_identifier": ["TEST123"], "category": ["Test"], "price": [10.0]})

        register_characteristics_function("custom", custom_characteristics)

        funcs = list_simulation_functions()
        assert "custom" in funcs["characteristics"]

        # Verify we can retrieve it
        func = get_simulation_function("characteristics", "custom")
        assert func is custom_characteristics

        # Clean up
        clear_simulation_registry()

    def test_enrichment_registry_works(self):
        """Test that enrichment registry functions work with new implementation."""
        from online_retail_simulator.enrich.enrichment_registry import (
            clear_enrichment_registry,
            list_enrichment_functions,
            register_enrichment_function,
        )

        clear_enrichment_registry()

        def custom_enrichment(metrics, **kwargs):
            return metrics

        register_enrichment_function("custom", custom_enrichment)

        funcs = list_enrichment_functions()
        assert "custom" in funcs

        # Clean up
        clear_enrichment_registry()
