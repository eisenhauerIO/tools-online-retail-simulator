# Examples

This section provides practical examples for common use cases with the Online Retail Simulator.

## Basic Usage Examples

### Simple Data Generation

Generate a basic dataset with rule-based simulation:

```python
from online_retail_simulator import simulate

# Generate 30 days of sales data
sales_df = simulate("demo/simulate/config_default_simulation.yaml")

# Explore the data
print(f"Generated {len(sales_df)} sales records")
print(f"Date range: {sales_df['date'].min()} to {sales_df['date'].max()}")
print(f"Categories: {sales_df['category'].unique()}")
print(f"Total revenue: ${sales_df['revenue'].sum():,.2f}")
```

### Two-Step Generation

For more control over the process:

```python
from online_retail_simulator import simulate_characteristics, simulate_metrics

# Step 1: Generate product catalog
products_df = simulate_characteristics("config.yaml")
print(f"Generated {len(products_df)} products")

# Step 2: Generate sales transactions
sales_df = simulate_metrics(products_df, "config.yaml")
print(f"Generated {len(sales_df)} sales records")
```

## Configuration Examples

### Minimal Configuration

```yaml
# minimal_config.yaml
SEED: 42
OUTPUT:
  DIR: "output"
  FILE_PREFIX: "minimal"
RULE:
  NUM_PRODUCTS: 20
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-07"
  SALE_PROB: 0.8
```

```python
sales_df = simulate("minimal_config.yaml")
```

### Large Dataset Configuration

```yaml
# large_dataset_config.yaml
SEED: 42
OUTPUT:
  DIR: "output"
  FILE_PREFIX: "large_dataset"
RULE:
  NUM_PRODUCTS: 1000
  DATE_START: "2024-01-01"
  DATE_END: "2024-12-31"
  SALE_PROB: 0.6
```

### ML-Based Generation

```yaml
# ml_config.yaml
SEED: 42
OUTPUT:
  DIR: "output"
  FILE_PREFIX: "ml_generated"
SYNTHESIZER:
  SYNTHESIZER_TYPE: "gaussian_copula"
  DEFAULT_PRODUCTS_ROWS: 200
  DEFAULT_SALES_ROWS: 5000
```

## Enrichment Examples

### Basic Enrichment Workflow

```python
from online_retail_simulator import simulate, enrich

# Generate baseline data
baseline_df = simulate("simulation_config.yaml")
print(f"Baseline revenue: ${baseline_df['revenue'].sum():,.2f}")

# Apply enrichment
enriched_df = enrich("enrichment_config.yaml", baseline_df)
print(f"Enriched revenue: ${enriched_df['revenue'].sum():,.2f}")

# Calculate lift
lift = (enriched_df['revenue'].sum() / baseline_df['revenue'].sum() - 1) * 100
print(f"Revenue lift: {lift:.1f}%")
```

### Enrichment Configuration

```yaml
# enrichment_config.yaml
IMPACT:
  FUNCTION: "combined_boost"
  PARAMS:
    effect_size: 0.3
    ramp_days: 5
    enrichment_fraction: 0.4
    enrichment_start: "2024-11-15"
    seed: 42
```

### Multiple Enrichment Scenarios

```python
from online_retail_simulator import simulate, enrich

# Generate baseline once
baseline_df = simulate("simulation_config.yaml")
baseline_revenue = baseline_df['revenue'].sum()

# Test multiple scenarios
scenarios = [
    {"effect_size": 0.1, "enrichment_fraction": 0.2},  # Conservative
    {"effect_size": 0.3, "enrichment_fraction": 0.3},  # Moderate
    {"effect_size": 0.5, "enrichment_fraction": 0.4},  # Aggressive
]

results = []
for i, params in enumerate(scenarios):
    # Create config for this scenario
    config = {
        "IMPACT": {
            "FUNCTION": "combined_boost",
            "PARAMS": {
                **params,
                "ramp_days": 7,
                "enrichment_start": "2024-11-15",
                "seed": 42
            }
        }
    }

    # Apply enrichment
    enriched_df = enrich(config, baseline_df)
    lift = (enriched_df['revenue'].sum() / baseline_revenue - 1) * 100

    results.append({
        "scenario": f"Scenario {i+1}",
        "effect_size": params["effect_size"],
        "enrichment_fraction": params["enrichment_fraction"],
        "revenue_lift": lift
    })

# Display results
for result in results:
    print(f"{result['scenario']}: {result['revenue_lift']:.1f}% lift")
```

## Analysis Examples

### Category Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt

# Generate data
sales_df = simulate("config.yaml")

# Revenue by category
category_revenue = sales_df.groupby('category')['revenue'].sum().sort_values(ascending=False)
print("Revenue by Category:")
print(category_revenue)

# Plot category performance
category_revenue.plot(kind='bar', title='Revenue by Category')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### Time Series Analysis

```python
# Daily sales trends
daily_sales = sales_df.groupby('date').agg({
    'quantity': 'sum',
    'revenue': 'sum'
}).reset_index()

daily_sales['date'] = pd.to_datetime(daily_sales['date'])

# Plot daily trends
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(daily_sales['date'], daily_sales['quantity'])
ax1.set_title('Daily Quantity Sold')
ax1.set_ylabel('Quantity')

ax2.plot(daily_sales['date'], daily_sales['revenue'])
ax2.set_title('Daily Revenue')
ax2.set_ylabel('Revenue ($)')

plt.tight_layout()
plt.show()
```

### Product Performance Analysis

```python
# Top performing products
product_performance = sales_df.groupby(['asin', 'category']).agg({
    'quantity': 'sum',
    'revenue': 'sum',
    'price': 'first'
}).reset_index()

# Top 10 products by revenue
top_products = product_performance.nlargest(10, 'revenue')
print("Top 10 Products by Revenue:")
print(top_products[['asin', 'category', 'revenue']])

# Revenue per unit analysis
product_performance['revenue_per_unit'] = product_performance['revenue'] / product_performance['quantity']
top_efficiency = product_performance.nlargest(10, 'revenue_per_unit')
print("\nMost Efficient Products (Revenue per Unit):")
print(top_efficiency[['asin', 'category', 'revenue_per_unit']])
```

## A/B Testing Examples

### Complete A/B Test Simulation

```python
from online_retail_simulator import simulate, enrich
import pandas as pd

def run_ab_test(simulation_config, enrichment_config, test_name):
    """Run a complete A/B test simulation"""

    # Generate control group (baseline)
    control_df = simulate(simulation_config)
    control_revenue = control_df['revenue'].sum()

    # Generate treatment group (enriched)
    treatment_df = enrich(enrichment_config, control_df)
    treatment_revenue = treatment_df['revenue'].sum()

    # Calculate metrics
    lift = (treatment_revenue / control_revenue - 1) * 100

    results = {
        'test_name': test_name,
        'control_revenue': control_revenue,
        'treatment_revenue': treatment_revenue,
        'absolute_lift': treatment_revenue - control_revenue,
        'relative_lift_pct': lift,
        'control_transactions': len(control_df),
        'treatment_transactions': len(treatment_df)
    }

    return results

# Run multiple tests
tests = [
    {
        'name': 'Conservative Test',
        'enrichment': {
            'IMPACT': {
                'FUNCTION': 'combined_boost',
                'PARAMS': {
                    'effect_size': 0.2,
                    'enrichment_fraction': 0.2,
                    'ramp_days': 3,
                    'enrichment_start': '2024-11-15',
                    'seed': 42
                }
            }
        }
    },
    {
        'name': 'Aggressive Test',
        'enrichment': {
            'IMPACT': {
                'FUNCTION': 'combined_boost',
                'PARAMS': {
                    'effect_size': 0.6,
                    'enrichment_fraction': 0.5,
                    'ramp_days': 7,
                    'enrichment_start': '2024-11-10',
                    'seed': 42
                }
            }
        }
    }
]

# Run all tests
simulation_config = "demo/simulate/config_default_simulation.yaml"
all_results = []

for test in tests:
    result = run_ab_test(simulation_config, test['enrichment'], test['name'])
    all_results.append(result)

# Display results
results_df = pd.DataFrame(all_results)
print("A/B Test Results:")
print(results_df[['test_name', 'relative_lift_pct', 'absolute_lift']])
```

### Statistical Significance Testing

```python
from scipy import stats
import numpy as np

def calculate_significance(control_df, treatment_df, metric='revenue'):
    """Calculate statistical significance of A/B test results"""

    # Daily aggregation for both groups
    control_daily = control_df.groupby('date')[metric].sum()
    treatment_daily = treatment_df.groupby('date')[metric].sum()

    # Ensure same date range
    common_dates = set(control_daily.index) & set(treatment_daily.index)
    control_values = [control_daily[date] for date in common_dates]
    treatment_values = [treatment_daily[date] for date in common_dates]

    # Perform t-test
    t_stat, p_value = stats.ttest_ind(treatment_values, control_values)

    # Calculate effect size (Cohen's d)
    pooled_std = np.sqrt(((len(control_values) - 1) * np.var(control_values) +
                         (len(treatment_values) - 1) * np.var(treatment_values)) /
                        (len(control_values) + len(treatment_values) - 2))
    cohens_d = (np.mean(treatment_values) - np.mean(control_values)) / pooled_std

    return {
        'p_value': p_value,
        'is_significant': p_value < 0.05,
        'cohens_d': cohens_d,
        'effect_size_interpretation': interpret_cohens_d(cohens_d)
    }

def interpret_cohens_d(d):
    """Interpret Cohen's d effect size"""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"

# Example usage
control_df = simulate("simulation_config.yaml")
treatment_df = enrich("enrichment_config.yaml", control_df)

significance_results = calculate_significance(control_df, treatment_df)
print(f"P-value: {significance_results['p_value']:.4f}")
print(f"Significant: {significance_results['is_significant']}")
print(f"Effect size: {significance_results['effect_size_interpretation']}")
```

## Custom Enrichment Functions

### Creating Custom Impact Functions

```python
from online_retail_simulator.enrich import register_enrichment_function

def seasonal_boost(df, peak_multiplier=2.0, peak_start="2024-11-20", peak_end="2024-11-30", **kwargs):
    """Custom seasonal boost function"""
    import pandas as pd

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    peak_start = pd.to_datetime(peak_start)
    peak_end = pd.to_datetime(peak_end)

    # Apply boost during peak period
    peak_mask = (df['date'] >= peak_start) & (df['date'] <= peak_end)
    df.loc[peak_mask, 'quantity'] *= peak_multiplier
    df.loc[peak_mask, 'revenue'] = df.loc[peak_mask, 'price'] * df.loc[peak_mask, 'quantity']

    return df

# Register the function
register_enrichment_function("seasonal_boost", seasonal_boost)

# Use in configuration
enrichment_config = {
    "IMPACT": {
        "FUNCTION": "seasonal_boost",
        "PARAMS": {
            "peak_multiplier": 1.5,
            "peak_start": "2024-11-25",
            "peak_end": "2024-11-30"
        }
    }
}
```

### Category-Specific Enrichment

```python
def category_specific_boost(df, category_effects=None, **kwargs):
    """Apply different effects to different categories"""
    if category_effects is None:
        category_effects = {
            'Electronics': 0.3,
            'Clothing': 0.2,
            'Books': 0.1
        }

    df = df.copy()

    for category, effect_size in category_effects.items():
        mask = df['category'] == category
        df.loc[mask, 'quantity'] *= (1 + effect_size)
        df.loc[mask, 'revenue'] = df.loc[mask, 'price'] * df.loc[mask, 'quantity']

    return df

# Register and use
register_enrichment_function("category_specific_boost", category_specific_boost)

enrichment_config = {
    "IMPACT": {
        "FUNCTION": "category_specific_boost",
        "PARAMS": {
            "category_effects": {
                "Electronics": 0.4,
                "Books": 0.2,
                "Clothing": 0.3
            }
        }
    }
}
```

## Integration Examples

### Jupyter Notebook Integration

```python
# Cell 1: Setup
%matplotlib inline
import pandas as pd
import matplotlib.pyplot as plt
from online_retail_simulator import simulate, enrich

# Cell 2: Generate data
sales_df = simulate("config.yaml")
print(f"Generated {len(sales_df)} records")
sales_df.head()

# Cell 3: Quick visualization
sales_df.groupby('category')['revenue'].sum().plot(kind='bar')
plt.title('Revenue by Category')
plt.show()

# Cell 4: Time series
daily_revenue = sales_df.groupby('date')['revenue'].sum()
daily_revenue.plot(title='Daily Revenue Trend')
plt.show()
```

### Pandas Integration

```python
# Seamless pandas integration
sales_df = simulate("config.yaml")

# Standard pandas operations work immediately
summary_stats = sales_df.describe()
category_pivot = sales_df.pivot_table(
    values='revenue',
    index='date',
    columns='category',
    aggfunc='sum'
)

# Export to various formats
sales_df.to_csv('sales_data.csv', index=False)
sales_df.to_parquet('sales_data.parquet')
sales_df.to_json('sales_data.json', orient='records')
```

These examples demonstrate the flexibility and power of the Online Retail Simulator for various data science and business analysis use cases.
