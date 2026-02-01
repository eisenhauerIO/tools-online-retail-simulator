"""Test that randomness is controlled via seed parameter."""

import copy

import pandas as pd

from online_retail_simulator.simulate.metrics_rule_based import simulate_metrics_rule_based
from online_retail_simulator.simulate.products_rule_based import simulate_products_rule_based


class TestRandomnessControl:
    """Verify seed parameter gives full control over randomness."""

    def test_default_produces_different_results(self, config_randomness_test):
        """Without seed, each run produces different results."""
        products1 = simulate_products_rule_based(config_randomness_test)
        products2 = simulate_products_rule_based(config_randomness_test)

        assert not products1.equals(products2), "Default should produce random results"

    def test_seed_produces_identical_results(self, config_randomness_test):
        """With seed set, each run produces identical results."""
        config = copy.deepcopy(config_randomness_test)
        config["RULE"]["PRODUCTS"]["PARAMS"]["seed"] = 42
        config["RULE"]["METRICS"]["PARAMS"]["seed"] = 42

        products1 = simulate_products_rule_based(config)
        products2 = simulate_products_rule_based(config)

        pd.testing.assert_frame_equal(products1, products2)

    def test_different_seeds_produce_different_results(self, config_randomness_test):
        """Different seeds produce different results."""
        config1 = copy.deepcopy(config_randomness_test)
        config1["RULE"]["PRODUCTS"]["PARAMS"]["seed"] = 42

        config2 = copy.deepcopy(config_randomness_test)
        config2["RULE"]["PRODUCTS"]["PARAMS"]["seed"] = 99

        products1 = simulate_products_rule_based(config1)
        products2 = simulate_products_rule_based(config2)

        assert not products1.equals(products2), "Different seeds should produce different results"

    def test_metrics_reproducibility_with_seed(self, config_randomness_test):
        """Metrics simulation is reproducible with seed."""
        config = copy.deepcopy(config_randomness_test)
        config["RULE"]["PRODUCTS"]["PARAMS"]["seed"] = 42
        config["RULE"]["METRICS"]["PARAMS"]["seed"] = 42

        products = simulate_products_rule_based(config)
        metrics1 = simulate_metrics_rule_based(products, config)
        metrics2 = simulate_metrics_rule_based(products, config)

        pd.testing.assert_frame_equal(metrics1, metrics2)
