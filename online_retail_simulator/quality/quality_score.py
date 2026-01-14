"""Quality score calculation for product data."""


def calculate_quality_score(product: dict) -> float:
    """
    Calculate quality score for a product (0.0 - 1.0).

    Score components:
    - Title quality (30%): Title length (up to 50 chars)
    - Description quality (35%): Description length (up to 100 chars)
    - Features quality (20%): Features list (up to 4 items)
    - Brand (15%): Brand field populated

    Args:
        product: Dictionary containing product data with title, description, features, brand

    Returns:
        Quality score between 0.0 and 1.0

    Raises:
        KeyError: If required product fields are missing
    """
    score = 0.0

    # Title quality (30%)
    title = product["title"]
    score += 0.30 * min(len(title) / 50, 1.0)

    # Description quality (35%)
    description = product["description"]
    score += 0.35 * min(len(description) / 100, 1.0)

    # Features quality (20%)
    features = product["features"]
    score += 0.20 * min(len(features) / 4, 1.0)

    # Brand (15%)
    brand = product["brand"]
    score += 0.15 if brand else 0.0

    return round(score, 3)
