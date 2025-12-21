"""
Interface for simulating product metrics.
Dispatches to rule-based implementation based on method argument.
"""

from ..config_processor import process_config
from ..manage import JobInfo, load_dataframe, save_dataframe, save_job_metadata


def simulate_metrics(job_info: JobInfo, config_path: str) -> JobInfo:
    """
    Simulate product metrics using the backend specified in config.

    Args:
        job_info: JobInfo containing products.csv
        config_path: Path to configuration file

    Returns:
        JobInfo: Same job, now also containing sales.csv
    """
    config = process_config(config_path)

    # Load products from job
    products_df = load_dataframe(job_info, "products")
    if products_df is None:
        raise FileNotFoundError(f"products.csv not found in job {job_info.job_id}")

    # Generate sales DataFrame
    sales_df = _generate_metrics(products_df, config)

    # Save sales to same job
    save_dataframe(job_info, "sales", sales_df)
    save_job_metadata(
        job_info,
        config,
        config_path,
        num_products=len(products_df),
        num_sales=len(sales_df),
    )

    return job_info


def _generate_metrics(product_characteristics, config: dict):
    """Generate metrics DataFrame based on config backend."""
    # Simple either/or logic: RULE or SYNTHESIZER, not both, not neither
    if "RULE" in config:
        if "SYNTHESIZER" in config:
            raise ValueError("Config cannot contain both RULE and SYNTHESIZER blocks")

        # Rule-based generation
        rule_config = config["RULE"]
        if "METRICS" not in rule_config:
            raise ValueError("RULE block must contain METRICS section")

        metrics_config = rule_config["METRICS"]
        function_name = metrics_config.get("FUNCTION", "default")

        from .rule_registry import get_simulation_function

        try:
            func = get_simulation_function("metrics", function_name)
        except KeyError as e:
            raise KeyError(f"Error in RULE.METRICS: {str(e)}") from e
        return func(product_characteristics, config)

    elif "SYNTHESIZER" in config:
        # Synthesizer-based generation
        synthesizer_config = config["SYNTHESIZER"]
        metrics_config = synthesizer_config["METRICS"]
        function_name = metrics_config.get("FUNCTION")

        if function_name != "gaussian_copula":
            raise NotImplementedError(f"Metrics function '{function_name}' not implemented")

        from .metrics_synthesizer_based import simulate_metrics_synthesizer_based

        return simulate_metrics_synthesizer_based(product_characteristics, config)

    else:
        # Hard failure - no valid configuration
        raise ValueError("Config must contain either RULE or SYNTHESIZER block")
