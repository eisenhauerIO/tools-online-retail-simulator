"""
Synthesizer-based simulation backend.
Reads a DataFrame from the path specified in config['SYNTHESIZER']['dataframe_path'].
No error handling, hard failures only.
"""

import random
import string

import pandas as pd


def generate_random_asin(prefix: str = "B") -> str:
    """Generate a random ASIN-like identifier.
    - 10 characters total
    - Alphanumeric
    - Defaults to starting with 'B' (common for non-book ASINs)
    """
    chars = string.ascii_uppercase + string.digits
    return prefix + "".join(random.choice(chars) for _ in range(9))


def simulate_characteristics_synthesizer_based(config):
    try:
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import GaussianCopulaSynthesizer
    except ImportError:
        raise ImportError(
            "SDV is required for synthesizer-based simulation. "
            "Install with: pip install online-retail-simulator[synthesizer]"
        )

    synthesizer_config = config["SYNTHESIZER"]

    # Get characteristics config
    if "CHARACTERISTICS" not in synthesizer_config:
        raise ValueError("SYNTHESIZER block must contain CHARACTERISTICS section")
    char_config = synthesizer_config["CHARACTERISTICS"]

    # Get function (synthesizer type)
    synthesizer_type = char_config.get("FUNCTION")
    if not synthesizer_type:
        raise ValueError("FUNCTION is required in CHARACTERISTICS section")
    if synthesizer_type != "gaussian_copula":
        raise NotImplementedError(
            f"Synthesizer function '{synthesizer_type}' not implemented. " "Only 'gaussian_copula' is supported."
        )

    # Get parameters
    if "PARAMS" not in char_config:
        raise ValueError("PARAMS is required in CHARACTERISTICS section")
    params = char_config["PARAMS"]

    # Get required parameters
    training_data_path = params.get("training_data_path")
    if not training_data_path:
        raise ValueError("training_data_path is required in PARAMS")

    num_rows = params.get("num_rows")
    if not num_rows:
        raise ValueError("num_rows is required in PARAMS")

    seed = params.get("seed")
    if seed is None:
        raise ValueError("seed is required in PARAMS")

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
