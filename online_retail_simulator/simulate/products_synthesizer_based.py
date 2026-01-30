"""
Synthesizer-based product simulation.
Reads a DataFrame from the path specified in config['SYNTHESIZER']['dataframe_path'].
No error handling, hard failures only.
"""

from typing import Dict

import pandas as pd


def simulate_products_synthesizer_based(config: Dict) -> pd.DataFrame:
    """
    Generate synthetic products using Gaussian Copula synthesizer.
    Args:
        config: Complete configuration dictionary
    Returns:
        DataFrame of synthetic products
    """
    try:
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import GaussianCopulaSynthesizer
    except ImportError:
        raise ImportError(
            "SDV is required for synthesizer-based simulation. "
            "Install with: pip install online-retail-simulator[synthesizer]"
        )

    params = config["SYNTHESIZER"]["PRODUCTS"]["PARAMS"]
    training_data_path, num_rows, seed = (
        params["training_data_path"],
        params["num_rows"],
        params["seed"],
    )

    # Load training data
    training_data = pd.read_csv(training_data_path)

    # Step 1: Create metadata and synthesizer
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(training_data)
    synthesizer = GaussianCopulaSynthesizer(metadata)

    # Step 2: Train the synthesizer
    synthesizer.fit(training_data)

    # Step 3: Generate synthetic data with seed
    import numpy as np

    np.random.seed(seed)
    synthetic_data = synthesizer.sample(num_rows=num_rows)

    return synthetic_data
