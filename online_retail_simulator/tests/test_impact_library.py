"""Tests for enrichment impact library functions."""

import pandas as pd

from online_retail_simulator.enrich.enrichment_library import probability_boost, quantity_boost


def create_test_sales():
    """Create test sales data for impact function testing."""
    return [
        {
            "product_id": "PROD001",
            "date": "2024-11-10",
            "ordered_units": 2,
            "price": 100.0,
            "unit_price": 100.0,
            "revenue": 200.0,
        },
        {
            "product_id": "PROD001",
            "date": "2024-11-20",
            "ordered_units": 1,
            "price": 100.0,
            "unit_price": 100.0,
            "revenue": 100.0,
        },
        {
            "product_id": "PROD002",
            "date": "2024-11-15",
            "ordered_units": 3,
            "price": 50.0,
            "unit_price": 50.0,
            "revenue": 150.0,
        },
        {
            "product_id": "PROD002",
            "date": "2024-11-25",
            "ordered_units": 2,
            "price": 50.0,
            "unit_price": 50.0,
            "revenue": 100.0,
        },
        {
            "product_id": "PROD003",
            "date": "2024-11-12",
            "ordered_units": 1,
            "price": 200.0,
            "unit_price": 200.0,
            "revenue": 200.0,
        },
    ]


class TestQuantityBoost:
    """Test quantity_boost function."""

    def test_quantity_boost_basic(self):
        """Test basic ordered_units boost functionality."""
        sales = create_test_sales()

        result, potential_outcomes = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=42,
        )

        # Should return same number of sales
        assert len(result) == len(sales)

        # Should return potential outcomes DataFrame
        assert isinstance(potential_outcomes, pd.DataFrame)
        assert "product_identifier" in potential_outcomes.columns
        assert "date" in potential_outcomes.columns
        assert "Y0_revenue" in potential_outcomes.columns
        assert "Y1_revenue" in potential_outcomes.columns

        # Check that some sales after enrichment start have increased quantities
        post_enrichment = [s for s in result if s["date"] >= "2024-11-15"]
        original_post = [s for s in sales if s["date"] >= "2024-11-15"]

        total_ordered_units_original = sum(s["ordered_units"] for s in original_post)
        total_ordered_units_result = sum(s["ordered_units"] for s in post_enrichment)

        # Should have some increase due to enrichment
        assert total_ordered_units_result >= total_ordered_units_original

    def test_quantity_boost_no_enrichment_before_start(self):
        """Test that no enrichment is applied before start date."""
        sales = create_test_sales()

        result, _ = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=1.0,  # All products enriched
            enrichment_start="2024-12-01",  # After all sales
            seed=42,
        )

        # All sales should be unchanged since they're before start date
        for original, treated in zip(sales, result):
            assert treated["ordered_units"] == original["ordered_units"]
            assert treated["revenue"] == original["revenue"]

    def test_quantity_boost_zero_fraction(self):
        """Test that no enrichment is applied with zero fraction."""
        sales = create_test_sales()

        result, _ = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=0.0,  # No products enriched
            enrichment_start="2024-11-01",
            seed=42,
        )

        # All sales should be unchanged
        for original, treated in zip(sales, result):
            assert treated["ordered_units"] == original["ordered_units"]
            assert treated["revenue"] == original["revenue"]

    def test_quantity_boost_reproducibility(self):
        """Test that results are reproducible with same seed."""
        sales = create_test_sales()

        result1, po1 = quantity_boost(
            sales,
            effect_size=0.3,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=123,
        )

        result2, po2 = quantity_boost(
            sales,
            effect_size=0.3,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=123,
        )

        # Results should be identical
        assert result1 == result2
        # Potential outcomes should also be identical
        pd.testing.assert_frame_equal(po1, po2)

    def test_quantity_boost_different_seeds(self):
        """Test that different seeds can produce different results."""
        # Create more products to increase chance of different selection
        sales = []
        for i in range(10):
            sales.append(
                {
                    "product_id": f"PROD{i:03d}",
                    "date": "2024-11-20",
                    "ordered_units": 1,
                    "price": 100.0,
                    "unit_price": 100.0,
                    "revenue": 100.0,
                }
            )

        result1, _ = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=42,
        )

        result2, _ = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=999,
        )

        # With 10 products and 50% enrichment, different seeds should produce different results
        # (though not guaranteed, very likely)
        total_qty1 = sum(s["ordered_units"] for s in result1)
        total_qty2 = sum(s["ordered_units"] for s in result2)

        # At least verify that the function runs with different seeds
        assert len(result1) == len(result2) == 10
        # Results might be different (but not required for test to pass)
        assert total_qty1 >= 10  # At least original quantities
        assert total_qty2 >= 10  # At least original quantities

    def test_quantity_boost_revenue_calculation(self):
        """Test that revenue is correctly recalculated after ordered_units boost."""
        sales = [
            {
                "product_id": "PROD001",
                "date": "2024-11-20",
                "ordered_units": 2,
                "price": 100.0,
                "unit_price": 100.0,
                "revenue": 200.0,
            }
        ]

        result, _ = quantity_boost(
            sales,
            effect_size=0.5,  # 50% boost
            enrichment_fraction=1.0,  # All products enriched
            enrichment_start="2024-11-15",
            seed=42,
        )

        treated_sale = result[0]
        # Quantity should be boosted: 2 * 1.5 = 3
        assert treated_sale["ordered_units"] == 3
        # Revenue should be recalculated: 3 * 100 = 300
        assert treated_sale["revenue"] == 300.0

    def test_quantity_boost_default_parameters(self):
        """Test ordered_units boost with default parameters."""
        sales = create_test_sales()

        # Test with minimal parameters (should use defaults)
        result, potential_outcomes = quantity_boost(sales)

        assert len(result) == len(sales)
        assert isinstance(result, list)
        assert isinstance(potential_outcomes, pd.DataFrame)

    def test_quantity_boost_potential_outcomes_all_products(self):
        """Test that potential outcomes are generated for ALL products."""
        sales = create_test_sales()

        result, potential_outcomes = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=0.5,  # Only 50% treated
            enrichment_start="2024-11-15",
            seed=42,
        )

        # Potential outcomes should exist for all product-date combinations
        sales_product_dates = set((s["product_id"], s["date"]) for s in sales)
        po_product_dates = set(zip(potential_outcomes["product_identifier"], potential_outcomes["date"]))
        assert sales_product_dates == po_product_dates

        # Y1 should be >= Y0 for dates after enrichment start
        post_start = potential_outcomes[potential_outcomes["date"] >= "2024-11-15"]
        assert (post_start["Y1_revenue"] >= post_start["Y0_revenue"]).all()

        # Y1 should equal Y0 for dates before enrichment start
        pre_start = potential_outcomes[potential_outcomes["date"] < "2024-11-15"]
        assert (pre_start["Y1_revenue"] == pre_start["Y0_revenue"]).all()


class TestProbabilityBoost:
    """Test probability_boost function."""

    def test_probability_boost_delegates_to_quantity_boost(self):
        """Test that probability_boost delegates to quantity_boost."""
        sales = create_test_sales()

        prob_result, prob_po = probability_boost(
            sales,
            effect_size=0.3,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=42,
        )

        qty_result, qty_po = quantity_boost(
            sales,
            effect_size=0.3,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=42,
        )

        # Results should be identical since probability_boost calls quantity_boost
        assert prob_result == qty_result
        pd.testing.assert_frame_equal(prob_po, qty_po)

    def test_probability_boost_basic(self):
        """Test basic probability boost functionality."""
        sales = create_test_sales()

        result, potential_outcomes = probability_boost(
            sales,
            effect_size=0.4,
            enrichment_fraction=0.6,
            enrichment_start="2024-11-15",
            seed=123,
        )

        assert len(result) == len(sales)
        assert isinstance(potential_outcomes, pd.DataFrame)

        # Should have some impact on post-enrichment sales
        post_enrichment = [s for s in result if s["date"] >= "2024-11-15"]
        original_post = [s for s in sales if s["date"] >= "2024-11-15"]

        total_ordered_units_original = sum(s["ordered_units"] for s in original_post)
        total_ordered_units_result = sum(s["ordered_units"] for s in post_enrichment)

        assert total_ordered_units_result >= total_ordered_units_original


class TestImpactLibraryEdgeCases:
    """Test edge cases and error conditions for impact library."""

    def test_empty_sales_list(self):
        """Test impact functions with empty sales list."""
        empty_sales = []

        result_qty, po_qty = quantity_boost(empty_sales)
        result_prob, po_prob = probability_boost(empty_sales)

        assert result_qty == []
        assert result_prob == []
        assert len(po_qty) == 0
        assert len(po_prob) == 0

    def test_single_sale(self):
        """Test impact functions with single sale."""
        single_sale = [
            {
                "product_id": "PROD001",
                "date": "2024-11-20",
                "ordered_units": 1,
                "price": 50.0,
                "unit_price": 50.0,
                "revenue": 50.0,
            }
        ]

        result_qty, po_qty = quantity_boost(
            single_sale, enrichment_fraction=1.0, enrichment_start="2024-11-15", seed=42
        )
        result_prob, po_prob = probability_boost(
            single_sale, enrichment_fraction=1.0, enrichment_start="2024-11-15", seed=42
        )

        assert len(result_qty) == 1
        assert len(result_prob) == 1
        assert len(po_qty) == 1
        assert len(po_prob) == 1

    def test_missing_unit_price_fallback(self):
        """Test that functions handle missing unit_price by using price."""
        sales = [
            {
                "product_id": "PROD001",
                "date": "2024-11-20",
                "ordered_units": 2,
                "price": 75.0,
                # No unit_price field
                "revenue": 150.0,
            }
        ]

        result, _ = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=1.0,
            enrichment_start="2024-11-15",
            seed=42,
        )

        treated_sale = result[0]
        # Should use price as unit_price: 3 * 75 = 225
        assert treated_sale["ordered_units"] == 3
        assert treated_sale["revenue"] == 225.0

    def test_all_products_same_id(self):
        """Test impact functions when all sales have same product_id."""
        same_product_sales = [
            {
                "product_id": "PROD001",
                "date": "2024-11-15",
                "ordered_units": 1,
                "price": 100.0,
                "unit_price": 100.0,
                "revenue": 100.0,
            },
            {
                "product_id": "PROD001",
                "date": "2024-11-20",
                "ordered_units": 2,
                "price": 100.0,
                "unit_price": 100.0,
                "revenue": 200.0,
            },
        ]

        result, _ = quantity_boost(
            same_product_sales,
            effect_size=0.5,
            enrichment_fraction=0.5,  # 50% chance this product is enriched
            enrichment_start="2024-11-15",
            seed=42,
        )

        assert len(result) == 2
        # Either all sales are boosted or none (since same product)
        post_enrichment = [s for s in result if s["date"] >= "2024-11-15"]
        original_post = [s for s in same_product_sales if s["date"] >= "2024-11-15"]

        total_qty_original = sum(s["ordered_units"] for s in original_post)
        total_qty_result = sum(s["ordered_units"] for s in post_enrichment)

        # Should be either equal (not enriched) or greater (enriched)
        assert total_qty_result >= total_qty_original
