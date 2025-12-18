"""
Job-based storage utilities for saving simulation results.
"""

from .storage import save_simulation_data  # Legacy compatibility
from .storage import (
    cleanup_old_jobs,
    generate_job_id,
    get_job_directory,
    list_jobs,
    load_job_metadata,
    load_job_results,
    save_job_data,
)

__all__ = [
    "save_job_data",
    "load_job_results",
    "load_job_metadata",
    "list_jobs",
    "cleanup_old_jobs",
    "generate_job_id",
    "get_job_directory",
    "save_simulation_data",  # Legacy
]
