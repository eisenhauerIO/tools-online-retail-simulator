"""Mock product details generation (rule-based)."""

import random

import pandas as pd

# TODO: We need to merge this with the simulation of characteristics, so we have lists in scync.

# Mock data templates by category
MOCK_DATA = {
    "Electronics": {
        "brands": ["TechPro", "DigiMax", "SmartLife", "ElectraVolt", "NexGen"],
        "adjectives": ["Advanced", "Ultra", "Pro", "Smart", "Wireless"],
        "features": ["Long battery life", "Fast charging", "Bluetooth connectivity", "LCD display", "Voice control"],
    },
    "Home & Kitchen": {
        "brands": ["HomeStyle", "KitchenPro", "CozyLiving", "DomesticPlus", "ChefMate"],
        "adjectives": ["Premium", "Deluxe", "Essential", "Modern", "Classic"],
        "features": ["Dishwasher safe", "Heat resistant", "Non-stick coating", "Easy to clean", "Space saving"],
    },
    "Clothing": {
        "brands": ["UrbanWear", "StyleFit", "ComfortPlus", "TrendyThreads", "ClassicWear"],
        "adjectives": ["Comfortable", "Stylish", "Premium", "Casual", "Lightweight"],
        "features": ["Machine washable", "Breathable fabric", "Wrinkle resistant", "Stretch fit", "Quick dry"],
    },
    "default": {
        "brands": ["ValueBrand", "QualityFirst", "TrustMark", "PrimePick", "BestChoice"],
        "adjectives": ["Quality", "Premium", "Essential", "Classic", "Professional"],
        "features": ["High quality materials", "Durable construction", "Easy to use", "Great value", "Long lasting"],
    },
}

# Enhanced mock data for treatment mode (simulating "improved" product details)
MOCK_DATA_TREATMENT = {
    "Electronics": {
        "brands": ["TechPro Elite", "DigiMax Pro", "SmartLife AI", "ElectraVolt Plus", "NexGen Ultra"],
        "adjectives": ["Revolutionary", "AI-Powered", "Next-Generation", "Premium", "Cutting-Edge"],
        "features": [
            "Industry-leading battery life",
            "Lightning-fast charging",
            "Advanced Bluetooth 5.0",
            "Crystal-clear OLED display",
            "Intelligent voice assistant",
        ],
    },
    "Home & Kitchen": {
        "brands": ["HomeStyle Pro", "KitchenPro Elite", "CozyLiving Plus", "DomesticPlus Premium", "ChefMate Pro"],
        "adjectives": ["Award-Winning", "Chef-Recommended", "Eco-Friendly", "Designer", "Restaurant-Grade"],
        "features": [
            "Commercial-grade durability",
            "Premium heat distribution",
            "Advanced non-stick technology",
            "Effortless maintenance",
            "Compact space-saving design",
        ],
    },
    "Clothing": {
        "brands": ["UrbanWear Elite", "StyleFit Pro", "ComfortPlus Premium", "TrendyThreads Luxe", "ClassicWear Plus"],
        "adjectives": ["Luxurious", "Designer", "Eco-Conscious", "Performance", "Premium"],
        "features": [
            "Easy-care machine washable",
            "Advanced moisture-wicking fabric",
            "Permanent wrinkle-free technology",
            "4-way stretch comfort",
            "Rapid-dry technology",
        ],
    },
    "default": {
        "brands": ["ValueBrand Pro", "QualityFirst Elite", "TrustMark Premium", "PrimePick Plus", "BestChoice Pro"],
        "adjectives": ["Award-Winning", "Best-in-Class", "Premium", "Professional-Grade", "Industry-Leading"],
        "features": [
            "Premium-grade materials",
            "Enhanced durability",
            "Intuitive design",
            "Exceptional value",
            "Extended lifespan",
        ],
    },
}


def _get_mock_data(category: str, treatment_mode: bool = False) -> dict:
    """Get mock data templates for a category.

    Args:
        category: Product category
        treatment_mode: If True, use enhanced "treatment" templates

    Returns:
        Mock data dictionary with brands, adjectives, features
    """
    data_source = MOCK_DATA_TREATMENT if treatment_mode else MOCK_DATA
    for key in data_source:
        if key.lower() in category.lower():
            return data_source[key]
    return data_source["default"]


def simulate_product_details_mock(
    products_df: pd.DataFrame,
    seed: int = None,
    prompt_path: str = None,
    treatment_mode: bool = False,
) -> pd.DataFrame:
    """Generate mock product details (rule-based).

    Args:
        products_df: Input products with asin, category, price
        seed: Random seed for reproducibility
        prompt_path: Ignored for mock backend (accepted for API compatibility)
        treatment_mode: If True, generate "improved" product details

    Returns:
        DataFrame with added title, description, brand, features
    """
    # prompt_path is ignored for mock backend but accepted for API compatibility
    _ = prompt_path

    rng = random.Random(seed)
    results = []

    for product in products_df.to_dict("records"):
        category = product.get("category", "General")
        data = _get_mock_data(category, treatment_mode=treatment_mode)

        brand = rng.choice(data["brands"])
        adj = rng.choice(data["adjectives"])
        features = rng.sample(data["features"], min(4, len(data["features"])))

        title = f"{brand} {adj} {category} Item"
        if treatment_mode:
            description = f"Premium {category.lower()} product with exceptional quality. {features[0]}. {features[1]}."
        else:
            description = f"Quality {category.lower()} product for everyday use. {features[0]}. {features[1]}."

        results.append(
            {
                **product,
                "title": title,
                "description": description,
                "brand": brand,
                "features": features,
            }
        )

    return pd.DataFrame(results)
