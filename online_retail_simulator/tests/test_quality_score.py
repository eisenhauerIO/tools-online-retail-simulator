"""Tests for quality score calculation."""

import pytest

from online_retail_simulator.quality import calculate_quality_score


class TestCalculateQualityScore:
    """Test calculate_quality_score function."""

    def test_full_product_high_score(self):
        """Complete product with all fields should score 1.0."""
        product = {
            "title": "A" * 50,  # Full title score (30%)
            "description": "A" * 100,  # Full description score (35%)
            "features": ["F1", "F2", "F3", "F4"],  # Full features score (20%)
            "brand": "TechPro",  # Full brand score (15%)
        }
        score = calculate_quality_score(product)
        assert score == 1.0

    def test_minimal_product_zero_score(self):
        """Product with empty values should score 0."""
        product = {
            "title": "",
            "description": "",
            "features": [],
            "brand": "",
        }
        score = calculate_quality_score(product)
        assert score == 0.0

    def test_title_only(self):
        """Title contributes 30% of score."""
        product = {
            "title": "A" * 50,  # Full title
            "description": "",
            "features": [],
            "brand": "",
        }
        score = calculate_quality_score(product)
        assert score == 0.30

    def test_title_partial(self):
        """Partial title length scores proportionally."""
        product = {
            "title": "A" * 25,  # 25/50 = 0.5 * 0.30 = 0.15
            "description": "",
            "features": [],
            "brand": "",
        }
        score = calculate_quality_score(product)
        assert score == 0.15

    def test_description_only(self):
        """Description contributes 35% of score."""
        product = {
            "title": "",
            "description": "A" * 100,  # Full description
            "features": [],
            "brand": "",
        }
        score = calculate_quality_score(product)
        assert score == 0.35

    def test_features_only(self):
        """Features contribute 20% of score."""
        product = {
            "title": "",
            "description": "",
            "features": ["F1", "F2", "F3", "F4"],  # Full features
            "brand": "",
        }
        score = calculate_quality_score(product)
        assert score == 0.20

    def test_features_partial(self):
        """Partial features scores proportionally."""
        product = {
            "title": "",
            "description": "",
            "features": ["F1", "F2"],  # 2/4 = 0.5 * 0.20 = 0.10
            "brand": "",
        }
        score = calculate_quality_score(product)
        assert score == 0.10

    def test_brand_only(self):
        """Brand contributes 15% of score."""
        product = {
            "title": "",
            "description": "",
            "features": [],
            "brand": "TechPro",
        }
        score = calculate_quality_score(product)
        assert score == 0.15

    def test_score_is_rounded(self):
        """Score should be rounded to 3 decimal places."""
        product = {
            "title": "A" * 33,  # 33/50 = 0.66 * 0.30 = 0.198
            "description": "",
            "features": [],
            "brand": "",
        }
        score = calculate_quality_score(product)
        assert score == round(score, 3)

    def test_missing_title_raises_keyerror(self):
        """Missing title should raise KeyError."""
        product = {
            "description": "Test",
            "features": [],
            "brand": "",
        }
        with pytest.raises(KeyError):
            calculate_quality_score(product)

    def test_missing_description_raises_keyerror(self):
        """Missing description should raise KeyError."""
        product = {
            "title": "Test",
            "features": [],
            "brand": "",
        }
        with pytest.raises(KeyError):
            calculate_quality_score(product)

    def test_missing_features_raises_keyerror(self):
        """Missing features should raise KeyError."""
        product = {
            "title": "Test",
            "description": "Test",
            "brand": "",
        }
        with pytest.raises(KeyError):
            calculate_quality_score(product)

    def test_missing_brand_raises_keyerror(self):
        """Missing brand should raise KeyError."""
        product = {
            "title": "Test",
            "description": "Test",
            "features": [],
        }
        with pytest.raises(KeyError):
            calculate_quality_score(product)
