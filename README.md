# Online Retail Simulator

Generate synthetic retail data for testing, demos, and experimentation without exposing real business data.

## Quick Start

### 1. Install
```bash
# Basic installation
pip install -e .

# With ML-based generation (optional)
pip install -e ".[synthesizer]"

# For development
pip install -e ".[dev]"
```

### 2. Run Demo
```bash
python demo/example.py
```

### 3. Use in Code
```python
from online_retail_simulator import simulate

# Generate data using config file
sales_df = simulate("demo/config_rule.yaml")
print(f"Generated {len(sales_df)} sales records")
```

## Configuration

Create a YAML config file:

```yaml
SEED: 42

OUTPUT:
  DIR: output
  FILE_PREFIX: my_data

RULE:
  NUM_PRODUCTS: 50
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-30"
  SALE_PROB: 0.7
```

For ML-based generation:

```yaml
SEED: 42

OUTPUT:
  DIR: output
  FILE_PREFIX: my_data

SYNTHESIZER:
  SYNTHESIZER_TYPE: gaussian_copula
  DEFAULT_PRODUCTS_ROWS: 30
  DEFAULT_SALES_ROWS: 5000
```

## Programmatic Usage

```python
from online_retail_simulator import simulate

# One-step generation (recommended)
sales_df = simulate("config.yaml")

# Or step-by-step
from online_retail_simulator import simulate_characteristics, simulate_metrics

products_df = simulate_characteristics("config.yaml")
sales_df = simulate_metrics(products_df, "config.yaml")
```
## Enrichment (Treatment Effects)

Apply treatment effects to simulate catalog enrichment experiments. Effects are applied to:
- **Selected products only**: A fraction of products receive enrichment
- **Date-based**: Effects only apply to sales on/after the enrichment start date
- **Targeted impact**: Only sales of enriched products are modified

### Separated Workflow

```python
from online_retail_simulator import simulate, enrich

# Step 1: Generate base simulation data
sales_df = simulate("config_simulation.yaml")

# Step 2: Apply enrichment with treatment effects
enriched_df = enrich("config_enrichment.yaml", sales_df)
```

### Enrichment Config (config_enrichment.yaml)

```yaml
# Treatment impact specification
IMPACT:
  FUNCTION: "combined_boost"
  PARAMS:
    effect_size: 0.5
    ramp_days: 7
    enrichment_fraction: 0.3
    enrichment_start: "2024-11-15"
    seed: 42
```

### Available Impact Functions

- `quantity_boost` - Increase quantity sold by percentage
- `probability_boost` - Increase sale probability
- `combined_boost` - Gradual ramp-up effect with custom parameters

### Run Enrichment Demo

```bash
python demo/example_enrichment.py
```

## Features

- **Two modes**: Rule-based (simple) or ML-based (requires SDV)
- **Treatment effects**: Simulate catalog enrichment experiments
- **Reproducible**: Seed-controlled random generation
- **Realistic data**: 8 product categories, daily sales patterns
- **DataFrame output**: Returns pandas DataFrames
- **Python 3.8+**: Broad compatibility

## Data Structure

### Products DataFrame
```python
# Columns: asin, category, price
{
  "asin": "BRPOIG8F1C",
  "category": "Electronics",
  "price": 899.99
}
```

### Sales DataFrame
```python
# Columns: asin, category, price, date, quantity, revenue
{
  "asin": "BRPOIG8F1C",
  "category": "Electronics",
  "price": 899.99,
  "date": "2024-11-15",
  "quantity": 2,
  "revenue": 1799.98
}
```

## License

MIT
