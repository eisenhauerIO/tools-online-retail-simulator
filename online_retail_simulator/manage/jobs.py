"""
Job management functions for simulation data.

Generic job utilities (JobInfo, list_jobs, cleanup_old_jobs) are provided by artifact_store.
This module provides simulation-specific helpers that build on top of those primitives.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from artifact_store import (
    ArtifactStore,
    JobInfo,
    cleanup_old_jobs,
    generate_job_id,
    list_jobs,
)


def create_job(config: Dict, config_path: str, job_id: Optional[str] = None) -> JobInfo:
    """
    Create a new job directory with config.

    This is a simulation-specific wrapper that extracts storage path from config
    and copies the original config file to the job directory.

    Args:
        config: Configuration dictionary (expects STORAGE.PATH)
        config_path: Path to original config file
        job_id: Optional job ID, auto-generated if not provided

    Returns:
        JobInfo: Information about the created job
    """
    if job_id is None:
        job_id = generate_job_id()

    # Extract storage path from config
    storage_path = config.get("STORAGE", {}).get("PATH", ".")

    # Create JobInfo
    job_info = JobInfo(job_id=job_id, storage_path=storage_path)

    # Copy original config using ArtifactStore
    if Path(config_path).exists():
        store = job_info.get_store()
        source_store, filename = ArtifactStore.from_file_path(config_path)
        config_content = source_store.read_text(filename)
        store.write_text("config.yaml", config_content)

    return job_info


def save_job_metadata(job_info: JobInfo, config: Dict, config_path: str, **extra) -> None:
    """
    Save or update job metadata.

    Args:
        job_info: JobInfo for the job
        config: Configuration dictionary
        config_path: Path to original config file
        **extra: Additional metadata fields
    """
    store = job_info.get_store()

    metadata = {
        "job_id": job_info.job_id,
        "timestamp": datetime.now().isoformat(),
        "config_path": config_path,
        "storage_path": job_info.storage_path,
        "seed": config.get("SEED"),
        "mode": "RULE" if "RULE" in config else "SYNTHESIZER",
        "config": config,
        **extra,
    }

    store.write_json("metadata.json", metadata)


def save_job_data(
    products_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    config: Dict,
    config_path: str,
    job_id: Optional[str] = None,
) -> JobInfo:
    """
    Save simulation data with automatic job-based storage.

    Args:
        products_df: Product characteristics DataFrame
        sales_df: Sales metrics DataFrame
        config: Configuration dictionary
        config_path: Path to original config file
        job_id: Optional job ID, auto-generated if not provided

    Returns:
        JobInfo: Information about the saved job
    """
    job_info = create_job(config, config_path, job_id)

    # Use JobInfo.save_df method
    job_info.save_df("products", products_df)
    job_info.save_df("sales", sales_df)
    save_job_metadata(
        job_info,
        config,
        config_path,
        num_products=len(products_df),
        num_sales=len(sales_df),
    )

    return job_info


def load_job_results(job_info: JobInfo) -> Dict[str, pd.DataFrame]:
    """
    Load simulation results for a job.

    Args:
        job_info: JobInfo containing job details

    Returns:
        Dict with available DataFrames: 'products', 'sales', 'enriched'

    Raises:
        FileNotFoundError: If job directory doesn't exist
    """
    store = job_info.get_store()

    if not store.exists(""):
        raise FileNotFoundError(f"Job directory not found: {store.base_path}")

    results = {}
    for name in ["products", "sales", "enriched"]:
        df = job_info.load_df(name)
        if df is not None:
            results[name] = df

    return results


def load_job_metadata(job_info: JobInfo) -> Dict:
    """
    Load metadata for a job.

    Args:
        job_info: JobInfo containing job details

    Returns:
        Dict: Job metadata

    Raises:
        FileNotFoundError: If job directory or metadata file doesn't exist
    """
    store = job_info.get_store()

    if not store.exists("metadata.json"):
        raise FileNotFoundError(f"Metadata file not found: {store.full_path('metadata.json')}")

    return store.read_json("metadata.json")
