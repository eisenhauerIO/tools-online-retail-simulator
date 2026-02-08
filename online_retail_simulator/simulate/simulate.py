"""
Simulate workflow: combines products and metrics simulation.
"""

from typing import Optional

import pandas as pd

from ..config_processor import process_config
from ..manage import JobInfo, create_job, save_job_metadata
from .metrics import simulate_metrics
from .product_details import simulate_product_details
from .products import simulate_products


def simulate(
    config_path: str,
    products_df: Optional[pd.DataFrame] = None,
    job_id: Optional[str] = None,
) -> JobInfo:
    """
    Runs simulate_products (or uses provided products), optionally simulate_product_details,
    and simulate_metrics.

    All results are automatically saved to a job-based directory structure
    under the configured storage path.

    Args:
        config_path: Path to configuration file
        products_df: Optional DataFrame of existing products. If provided, skips
                     product generation and uses this DataFrame instead.
                     Expected columns: product_identifier, category, price
        job_id: Optional job ID, auto-generated if not provided

    Returns:
        JobInfo: Information about the saved job
    """
    config = process_config(config_path)

    if products_df is not None:
        # Use provided products instead of generating new ones
        job_info = create_job(config, config_path, job_id=job_id)
        job_info.save_df("products", products_df)
        save_job_metadata(job_info, config, config_path, num_products=len(products_df))
    else:
        # Generate new products
        job_info = simulate_products(config_path, job_id=job_id)

    if "PRODUCT_DETAILS" in config:
        job_info = simulate_product_details(job_info, config_path)

    job_info = simulate_metrics(job_info, config_path)
    return job_info
