"""Tests for the rule registry system."""

import pandas as pd
import pytest

from online_retail_simulator.simulate import (
    get_simulation_function,
    list_simulation_functions,
    register_metrics_function,
    register_products_function,
)
from online_retail_simulator.simulate.rule_registry import clear_simulation_registry


def test_products_function_registration():
    """Test registering and retrieving products functions."""
    clear_simulation_registry()

    def dummy_products(config):
        return pd.DataFrame({"product_identifier": ["A123"], "category": ["Test"], "price": [10.0]})

    register_products_function("test_products", dummy_products)

    func = get_simulation_function("products", "test_products")
    assert func == dummy_products

    functions = list_simulation_functions()
    assert "test_products" in functions["products"]


def test_metrics_function_registration():
    """Test registering and retrieving metrics functions."""
    clear_simulation_registry()

    def dummy_metrics(products, config, **kwargs):
        return pd.DataFrame(
            {
                "product_identifier": ["A123"],
                "category": ["Test"],
                "price": [10.0],
                "date": ["2024-01-01"],
                "quantity": [1],
                "revenue": [10.0],
            }
        )

    register_metrics_function("test_metrics", dummy_metrics)

    func = get_simulation_function("metrics", "test_metrics")
    assert func == dummy_metrics

    functions = list_simulation_functions()
    assert "test_metrics" in functions["metrics"]


def test_invalid_function_signatures():
    """Test that functions with invalid signatures are rejected."""
    clear_simulation_registry()

    def invalid_products():  # Missing required parameters
        return pd.DataFrame()

    def invalid_metrics(wrong_param):  # Missing required parameters
        return pd.DataFrame()

    with pytest.raises(ValueError, match="must have parameters"):
        register_products_function("invalid", invalid_products)

    with pytest.raises(ValueError, match="must have parameters"):
        register_metrics_function("invalid", invalid_metrics)


def test_get_simulation_function():
    """Test the convenience function for getting registered functions."""
    clear_simulation_registry()

    def dummy_products(config):
        return pd.DataFrame()

    def dummy_metrics(products, config, **kwargs):
        return pd.DataFrame()

    register_products_function("test_products", dummy_products)
    register_metrics_function("test_metrics", dummy_metrics)

    products_func = get_simulation_function("products", "test_products")
    assert products_func == dummy_products

    metrics_func = get_simulation_function("metrics", "test_metrics")
    assert metrics_func == dummy_metrics

    with pytest.raises(ValueError, match="Invalid function type"):
        get_simulation_function("invalid", "test_products")


def test_list_all_functions():
    """Test listing all registered functions."""
    clear_simulation_registry()

    def dummy_products(config):
        return pd.DataFrame()

    def dummy_metrics(products, config, **kwargs):
        return pd.DataFrame()

    register_products_function("test_products", dummy_products)
    register_metrics_function("test_metrics", dummy_metrics)

    all_functions = list_simulation_functions()

    assert "products" in all_functions
    assert "metrics" in all_functions
    assert "test_products" in all_functions["products"]
    assert "test_metrics" in all_functions["metrics"]


def test_function_not_found():
    """Test error handling for non-existent functions."""
    clear_simulation_registry()

    with pytest.raises(KeyError, match="not registered"):
        get_simulation_function("products", "nonexistent")

    with pytest.raises(KeyError, match="not registered"):
        get_simulation_function("metrics", "nonexistent")


def test_clear_registry():
    """Test clearing the registry."""
    clear_simulation_registry()

    def dummy_products(config):
        return pd.DataFrame()

    register_products_function("test", dummy_products)

    functions = list_simulation_functions()
    assert "test" in functions["products"]
    assert "simulate_products_rule_based" in functions["products"]
    assert len(functions["products"]) == 2

    clear_simulation_registry()
    functions = list_simulation_functions()
    assert functions["products"] == ["simulate_products_rule_based"]
    assert functions["metrics"] == ["simulate_metrics_rule_based"]


def test_default_functions_registered():
    """Test that default functions are automatically registered."""
    clear_simulation_registry()

    functions = list_simulation_functions()

    assert "simulate_products_rule_based" in functions["products"]
    assert "simulate_metrics_rule_based" in functions["metrics"]

    products_func = get_simulation_function("products", "simulate_products_rule_based")
    metrics_func = get_simulation_function("metrics", "simulate_metrics_rule_based")

    assert products_func is not None
    assert metrics_func is not None
