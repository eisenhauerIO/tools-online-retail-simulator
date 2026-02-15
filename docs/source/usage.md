# Usage

## Workflow

Every simulation follows the same steps regardless of which backend is used.

**1. Write a YAML configuration file.** The config selects a generation backend (`RULE` or `SYNTHESIZER`), sets the parameters for product characteristics and metrics, and optionally configures storage. See [Configuration](configuration.md) for the full parameter reference.

```yaml
STORAGE:
  PATH: "output/demo"

RULE:
  CHARACTERISTICS:
    FUNCTION: simulate_characteristics_rule_based
    PARAMS:
      num_products: 50
      seed: 42
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-01-01"
      date_end: "2024-01-31"
      sale_prob: 0.7
```

**2. Run the simulation.**

```python
from online_retail_simulator import simulate

job_info = simulate("config.yaml")
```

The simulator generates product characteristics, adds product details (title, description, brand, features), and produces daily or weekly sales metrics. The return value is a `JobInfo` object that tracks all output artifacts.

**3. Load and inspect results.**

```python
from online_retail_simulator import load_job_results

results = load_job_results(job_info)
products_df = results["products"]
metrics_df = results["metrics"]
```

---

## Output

Each run creates a job directory under the configured storage path, named `job-YYYYMMDD-HHMMSS-{uuid}`. The directory contains:

| File | Description |
|------|-------------|
| `products.csv` | Product catalog with characteristics, titles, descriptions, brands, and features |
| `sales.csv` | Daily or weekly sales metrics per product |
| `metadata.json` | Job metadata including configuration, timestamps, and row counts |
| `config.yaml` | Copy of the configuration used for this run |

Products include a `quality_score` (0.0 to 1.0) reflecting data completeness based on title, description, features, and brand. The score affects conversion probability in metrics simulation.

---

## Optional: Enrichment

Enrichment applies controlled treatment effects to simulated data. This is useful for testing causal inference pipelines against known ground truth.

**1. Write an enrichment configuration.**

```yaml
IMPACT:
  FUNCTION: "combined_boost"
  PARAMS:
    effect_size: 0.5
    ramp_days: 7
    enrichment_fraction: 0.3
    enrichment_start: "2024-01-15"
    seed: 42
```

**2. Apply enrichment to an existing simulation.**

```python
from online_retail_simulator import enrich

enriched_job = enrich("enrichment_config.yaml", job_info)
```

---

## Available Backends

Each backend generates product characteristics and sales metrics using a different strategy.

| Backend | Config Key | Description |
|---------|------------|-------------|
| Rule-based | `RULE` | Deterministic generation using configurable rules and probability distributions |
| Synthesizer-based | `SYNTHESIZER` | ML-based generation using SDV (Synthetic Data Vault) learned from real data |

---

## Available Enrichment Functions

| Function | Description |
|----------|-------------|
| `combined_boost` | Gradual rollout with ramp-up period and partial product treatment (most realistic) |
| `quantity_boost` | Immediate multiplicative increase in ordered units |
| `probability_boost` | Alias for `quantity_boost` (probability reflected in quantity for existing records) |

Custom enrichment functions can be registered at runtime. See [Configuration](configuration.md) for parameter details.
