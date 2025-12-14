"""
Rule-based product metrics simulation (minimal skeleton).
"""
import pandas as pd
from typing import Any

def simulate_metrics_rule_based(product_characteristics: pd.DataFrame, config_path: str, **kwargs) -> pd.DataFrame:
    """
    Generate synthetic daily product metrics (rule-based).
    Args:
        product_characteristics: DataFrame of product characteristics
        config_path: Path to JSON configuration file
    Returns:
        DataFrame of product metrics (one row per product per date, with all characteristics)
    """
    from .config_processor import process_config
    import random
    from datetime import datetime, timedelta

    config = process_config(config_path)
    rule_config = config["RULE"]
    date_start = rule_config.get("DATE_START")
    date_end = rule_config.get("DATE_END")
    sale_probability = rule_config.get("SALE_PROB", 0.7)
    seed = config.get("SEED", 42)
    if seed is not None:
        random.seed(seed)

    start_date = datetime.strptime(date_start, "%Y-%m-%d")
    end_date = datetime.strptime(date_end, "%Y-%m-%d")

    rows = []
    current_date = start_date
    while current_date <= end_date:
        for _, prod in product_characteristics.iterrows():
            sale_occurred = random.random() < sale_probability
            if sale_occurred:
                quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
                revenue = round(prod["price"] * quantity, 2)
            else:
                quantity = 0
                revenue = 0.0
            row = prod.to_dict()
            row["date"] = current_date.strftime("%Y-%m-%d")
            row["quantity"] = quantity
            row["revenue"] = revenue
            rows.append(row)
        current_date += timedelta(days=1)
    return pd.DataFrame(rows)
