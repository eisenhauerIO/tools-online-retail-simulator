"""
Simple storage functions for simulation data.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

import pandas as pd


def save_simulation_data(
    products_df: pd.DataFrame, sales_df: pd.DataFrame, storage_path: str, config: Dict, config_path: str
) -> None:
    """
    Save simulation data to CSV files with metadata.

    Args:
        products_df: Product characteristics DataFrame
        sales_df: Sales metrics DataFrame
        storage_path: Directory path to save files
        config: Configuration dictionary
        config_path: Path to original config file
    """
    # Create storage directory
    path = Path(storage_path)
    path.mkdir(parents=True, exist_ok=True)

    # Save data files
    products_df.to_csv(path / "products.csv", index=False)
    sales_df.to_csv(path / "sales.csv", index=False)

    # Create metadata
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "config_path": config_path,
        "seed": config.get("SEED"),
        "mode": "RULE" if "RULE" in config else "SYNTHESIZER",
        "num_products": len(products_df),
        "num_sales": len(sales_df),
        "config": config,
    }

    # Save metadata
    with open(path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, default=str)
