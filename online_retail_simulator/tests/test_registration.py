"""Tests for enrichment function registration."""

import os
import tempfile

import pytest

from online_retail_simulator import (
    clear_enrichment_registry,
    enrich,
    list_enrichment_functions,
    register_enrichment_function,
    register_enrichment_module,
    simulate,
)


def test_register_function_direct():
    """Test direct function registration."""

    def test_effect(metrics, **kwargs):
        """Simple test effect."""
        multiplier = kwargs.get("multiplier", 1.5)
        for record in metrics:
            record["quantity"] = int(record["quantity"] * multiplier)
        return metrics

    # Register function
    register_enrichment_function("test_effect", test_effect)

    # Verify it's registered
    assert "test_effect" in list_enrichment_functions()


def test_register_function_invalid_signature():
    """Test registration with invalid function signature."""

    def bad_function(data, **kwargs):  # Missing 'metrics' parameter
        return data

    # Should raise error for invalid signature
    with pytest.raises(ValueError, match="must have parameters"):
        register_enrichment_function("bad_function", bad_function)


def test_register_module():
    """Test module registration."""
    # Clear registry first
    clear_enrichment_registry()

    # Register the enrichment library module
    register_enrichment_module("enrich.enrichment_library")

    # Should have registered the built-in functions
    registered = list_enrichment_functions()
    assert "quantity_boost" in registered
    assert "probability_boost" in registered
    assert "product_detail_boost" in registered


def test_use_registered_function():
    """Test using a registered function in enrichment."""

    def double_quantity(metrics, **kwargs):
        """Double the ordered units of all records."""
        for record in metrics:
            record["ordered_units"] = record["ordered_units"] * 2
            unit_price = record.get("unit_price", record.get("price"))
            record["revenue"] = round(record["ordered_units"] * unit_price, 2)
        return metrics

    # Register function
    register_enrichment_function("double_quantity", double_quantity)

    # Create test config
    config_content = """
IMPACT:
  FUNCTION: "double_quantity"
  PARAMS: {}
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info = simulate(test_config_path)

        # Load original sales before enrichment
        original_metrics = job_info.load_df("metrics")

        # Apply enrichment using registered function
        enriched_job_info = enrich(config_path, job_info)

        # Load enriched results
        enriched_metrics = enriched_job_info.load_df("enriched")

        # Verify doubling effect
        original_total = original_metrics["ordered_units"].sum()
        enriched_total = enriched_metrics["ordered_units"].sum()

        assert enriched_total == original_total * 2

    finally:
        os.unlink(config_path)


@pytest.mark.xfail(reason="Registry precedence over built-in functions needs investigation")
def test_registry_precedence():
    """Test that registry takes precedence over module loading."""

    # Clear registry first to ensure clean state
    clear_enrichment_registry()

    def custom_quantity_boost(metrics, **kwargs):
        """Custom version that triples all quantities."""
        import copy

        treated_metrics = []
        for record in metrics:
            record_copy = copy.deepcopy(record)
            record_copy["quantity"] = record_copy["quantity"] * 3
            unit_price = record_copy.get("unit_price", record_copy.get("price"))
            record_copy["revenue"] = round(record_copy["quantity"] * unit_price, 2)
            treated_metrics.append(record_copy)
        return treated_metrics

    # Register function with same name as built-in
    register_enrichment_function("quantity_boost", custom_quantity_boost)

    # Verify it was registered
    functions = list_enrichment_functions()
    assert "quantity_boost" in functions

    # Create test config using quantity_boost
    config_content = """
IMPACT:
  FUNCTION: "quantity_boost"
  PARAMS: {}
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info = simulate(test_config_path)

        # Load original sales before enrichment
        original_metrics = job_info.load_df("metrics")

        # Apply enrichment - should use registered version (triple)
        enriched_job_info = enrich(config_path, job_info)

        # Load enriched results
        enriched_metrics = enriched_job_info.load_df("enriched")

        # Verify tripling effect (not the built-in boost)
        original_total = original_metrics["quantity"].sum()
        enriched_total = enriched_metrics["quantity"].sum()

        assert enriched_total == original_total * 3

    finally:
        os.unlink(config_path)


def test_list_functions():
    """Test listing registered functions."""
    # Clear registry
    clear_enrichment_registry()

    # After clear, list() triggers lazy loading of defaults
    defaults = list_enrichment_functions()
    assert len(defaults) == 3  # quantity_boost, probability_boost, product_detail_boost

    # Register some custom functions
    def func1(metrics, **kwargs):
        return metrics

    def func2(metrics, **kwargs):
        return metrics

    register_enrichment_function("func1", func1)
    register_enrichment_function("func2", func2)

    # Should list defaults + custom
    functions = list_enrichment_functions()
    assert "func1" in functions
    assert "func2" in functions
    assert "quantity_boost" in functions
    assert len(functions) == 5  # 3 defaults + 2 custom


def test_register_function_overwrites():
    """Test that registering same name overwrites previous function."""

    def first_func(metrics, **kwargs):
        return [{"test": "first"}]

    def second_func(metrics, **kwargs):
        return [{"test": "second"}]

    # Register first function
    register_enrichment_function("test_func", first_func)

    # Register second function with same name
    register_enrichment_function("test_func", second_func)

    # Should only have one entry
    functions = list_enrichment_functions()
    count = sum(1 for f in functions if f == "test_func")
    assert count == 1

    # Should use the second function
    from online_retail_simulator.enrich.enrichment_registry import _enrichment_registry

    result = _enrichment_registry.get("test_func")([], test="value")
    assert result == [{"test": "second"}]
