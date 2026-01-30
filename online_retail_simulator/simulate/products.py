"""
Interface for simulating products.
Dispatches to appropriate backend based on config.
"""

from ..config_processor import process_config
from ..core.backends import BackendRegistry
from ..manage import create_job, save_job_metadata


def simulate_products(config_path: str):
    """
    Simulate products using the backend specified in config.

    Args:
        config_path: Path to configuration file

    Returns:
        JobInfo: Job containing products.csv
    """
    config = process_config(config_path)

    # Generate products DataFrame via backend
    backend = BackendRegistry.detect_backend(config)
    products_df = backend.simulate_products()

    # Create job and save products
    job_info = create_job(config, config_path)
    job_info.save_df("products", products_df)
    save_job_metadata(job_info, config, config_path, num_products=len(products_df))

    return job_info
