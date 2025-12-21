"""
Simulate workflow: combines characteristics and metrics simulation.
"""

from ..manage import JobInfo
from .characteristics import simulate_characteristics
from .metrics import simulate_metrics


def simulate(config_path: str) -> JobInfo:
    """
    Runs simulate_characteristics and simulate_metrics in sequence.

    All results are automatically saved to a job-based directory structure
    under the configured storage path.

    Args:
        config_path: Path to configuration file

    Returns:
        JobInfo: Information about the saved job
    """
    job_info = simulate_characteristics(config_path)
    job_info = simulate_metrics(job_info, config_path)
    return job_info
