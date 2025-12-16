"""
Synthesizer-based simulation backend.
Reads a DataFrame from the path specified in config['SYNTHESIZER']['dataframe_path'].
No error handling, hard failures only.
"""

import pandas as pd


def simulate_characteristics_synthesizer_based(config):
    try:
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import CTGANSynthesizer, GaussianCopulaSynthesizer, TVAESynthesizer
    except ImportError:
        raise ImportError(
            "SDV is required for synthesizer-based simulation. "
            "Install with: pip install online-retail-simulator[synthesizer]"
        )

    # For now, create dummy data since dataframe_path is not in config
    # This is a placeholder implementation
    import numpy as np

    np.random.seed(config.get("SEED", 42))
    num_rows = config["SYNTHESIZER"].get("DEFAULT_PRODUCTS_ROWS", 10)

    # Create dummy product data for demonstration
    categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
    products = []
    for i in range(num_rows):
        products.append(
            {
                "product_id": f"PROD{i:04d}",
                "name": f"Product {i}",
                "category": np.random.choice(categories),
                "price": np.random.uniform(10, 1000),
            }
        )

    synthetic_df = pd.DataFrame(products)
    return synthetic_df
