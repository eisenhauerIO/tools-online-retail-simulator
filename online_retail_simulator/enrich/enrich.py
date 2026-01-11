"""
Enrich workflow: applies enrichment treatments to sales data.
"""

from ..config_processor import process_config
from ..manage import JobInfo, save_job_metadata
from .enrichment import enrich as apply_enrichment


def enrich(config_path: str, job_info: JobInfo) -> JobInfo:
    """
    Apply enrichment to sales data using a config file.

    Saves enriched results to the same job directory.

    Args:
        config_path: Path to enrichment config (YAML or JSON)
        job_info: JobInfo object to load sales data from

    Returns:
        JobInfo: Same job, now also containing enriched.csv and optionally potential_outcomes.csv
    """
    # Load config
    config = process_config(config_path)

    # Load sales from job
    sales_df = job_info.load_df("sales")
    if sales_df is None:
        raise FileNotFoundError(f"sales.csv not found in job {job_info.job_id}")

    # Load products from job (optional, for product-aware enrichment functions)
    products_df = job_info.load_df("products")

    # Apply enrichment (pass job_info and products for product-aware functions)
    enriched_df, potential_outcomes_df = apply_enrichment(
        config_path, sales_df, job_info=job_info, products_df=products_df
    )

    # Save enriched to same job
    job_info.save_df("enriched", enriched_df)

    # Save potential outcomes if provided by the enrichment function
    if potential_outcomes_df is not None:
        job_info.save_df("potential_outcomes", potential_outcomes_df)

    # Update metadata
    save_job_metadata(job_info, config, config_path, is_enriched=True)

    return job_info
