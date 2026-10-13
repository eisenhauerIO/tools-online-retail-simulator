"""Product details simulation with backend dispatch."""

from ..config_processor import process_config
from ..manage import JobInfo, save_job_metadata
from .product_details_mock import simulate_product_details_mock
from .product_details_ollama import simulate_product_details_ollama

# Registry of product details backends
PRODUCT_DETAILS_REGISTRY = {
    "simulate_product_details_mock": simulate_product_details_mock,
    "simulate_product_details_ollama": simulate_product_details_ollama,
}


def simulate_product_details(job_info: JobInfo, config_path: str) -> JobInfo:
    """
    Simulate product details using configured backend.

    Loads existing products, enriches with title/description/brand/features,
    and saves back to the same job.

    Config example:
        PRODUCT_DETAILS:
          FUNCTION: simulate_product_details_mock  # or simulate_product_details_ollama

    The mock backend reuses the products seed, so a seeded config yields the same
    brands, features, and quality scores on every run.

    Args:
        job_info: Job containing products.csv
        config_path: Path to configuration file

    Returns:
        JobInfo: Same job with updated products.csv
    """
    config = process_config(config_path)
    product_details_config = config.get("PRODUCT_DETAILS", {})
    function_name = product_details_config.get("FUNCTION", "simulate_product_details_mock")

    if function_name not in PRODUCT_DETAILS_REGISTRY:
        raise ValueError(f"Unknown product details function: {function_name}")

    backend_fn = PRODUCT_DETAILS_REGISTRY[function_name]
    products_df = job_info.load_df("products")
    if backend_fn is simulate_product_details_mock:
        detailed_df = backend_fn(products_df, seed=_products_seed(config))
    else:
        detailed_df = backend_fn(products_df)

    job_info.save_df("products", detailed_df)
    save_job_metadata(job_info, config, config_path, has_product_details=True)

    return job_info


def _products_seed(config: dict):
    """Return the seed of the configured products phase, or None if unseeded."""
    for backend in ("RULE", "SYNTHESIZER"):
        if backend in config:
            return config[backend].get("PRODUCTS", {}).get("PARAMS", {}).get("seed")
    return None
