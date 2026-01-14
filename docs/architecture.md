# Architecture

The Online Retail Simulator follows a modular, configuration-driven architecture that supports multiple generation modes and extensible enrichment capabilities.

## Core Design Principles

### 1. Configuration-Driven Workflow
All simulation behavior is controlled through YAML configuration files, enabling:
- Reproducible experiments with version-controlled configs
- Easy parameter sweeps and scenario testing
- Clear separation of logic and parameters

### 2. Modular Architecture
The system is organized into distinct, loosely-coupled modules:
- **Core**: Shared infrastructure including `FunctionRegistry` for extensible function registration
- **Simulation**: Core data generation logic
- **Enrichment**: Treatment effect application
- **Configuration**: Parameter processing and validation
- **Storage**: Data persistence and retrieval

### 3. Mode-Based Generation
Two complementary approaches for different use cases:
- **Rule-based**: Deterministic, interpretable patterns
- **Synthesizer-based**: ML-learned patterns from real data

### 4. Reproducible Output
Seed-based deterministic generation ensures:
- Consistent results across runs
- Reliable A/B testing scenarios
- Debuggable data generation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Configuration Layer                       │
├─────────────────────────────────────────────────────────────┤
│  config_processor.py  │  config_defaults.yaml              │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     Simulation Layer                        │
├─────────────────────────────────────────────────────────────┤
│  simulate.py (orchestrator)                                 │
│  ├── simulate_characteristics.py                            │
│  │   ├── characteristics_rule_based.py                      │
│  │   └── characteristics_synthesizer_based.py               │
│  └── simulate_metrics.py                                    │
│      ├── metrics_rule_based.py                              │
│      └── metrics_synthesizer_based.py                       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Enrichment Layer                         │
├─────────────────────────────────────────────────────────────┤
│  enrich.py (orchestrator)                                   │
│  ├── enrichment.py                                          │
│  ├── enrichment_library.py                                  │
│  └── enrichment_registry.py                                 │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     Storage Layer                           │
├─────────────────────────────────────────────────────────────┤
│  JSON/CSV export  │  Pandas DataFrames  │  Pickle models   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Configuration Processing
```python
# config_processor.py
def load_config(config_path):
    """Load and validate configuration with defaults"""
    config = yaml.load(config_path)
    return merge_with_defaults(config)
```

### 2. Quality Score

Products include a `quality_score` (0.0 - 1.0) that reflects data quality based on
title, description, features, and brand. The score is calculated after product details
are generated (not after characteristics, since there's no content to evaluate).

| Stage | Typical Score | Reason |
|-------|---------------|--------|
| After characteristics | N/A | No quality_score (only identifier, category, price) |
| After product details | ~0.70-0.85 | Title, description, brand, features added |
| After enrichment (treated) | ~0.85+ | Enhanced content (if quality_boost applied) |

**Score Components:**
- Title quality (30%): Title length (up to 50 chars)
- Description quality (35%): Description length (up to 100 chars)
- Features quality (20%): Features list (up to 4 items)
- Brand (15%): Brand field populated

**Impact on Metrics:**
Quality score affects conversion probability in metrics simulation. If quality_score
is not present (e.g., right after characteristics), a neutral default of 0.5 is used:
```python
# Maps quality_score [0,1] to multiplier [0.8, 1.2]
# Default 0.5 = multiplier 1.0 (no effect)
quality_score = product.get("quality_score", 0.5)
quality_multiplier = 0.8 + (quality_score * 0.4)
adjusted_sale_prob = sale_prob * quality_multiplier
```

### 3. Two-Phase Generation

#### Phase 1: Product Characteristics
```python
# Generate product catalog, returns JobInfo
job_info = simulate_characteristics(config)
# Output: JobInfo (products.csv saved to job directory)
results = load_job_results(job_info)
products_df = results["products"]
```

#### Phase 2: Product Metrics
```python
# Generate product metrics, takes JobInfo
job_info = simulate_metrics(job_info, config)
# Output: JobInfo (metrics.csv saved to job directory)
results = load_job_results(job_info)
metrics_df = results["metrics"]
```

### 4. Optional Enrichment
```python
# Apply treatment effects
enriched_job = enrich("enrichment_config.yaml", baseline_job)
# Output: JobInfo for enriched results
```

Enrichment functions can optionally update `quality_score` for treated products
using the `quality_boost` parameter:
```yaml
IMPACT:
  FUNCTION: "product_detail_boost"
  PARAMS:
    quality_boost: 0.15  # Optional: adds +0.15 to treated products' quality_score
```


## Backend Plugin Architecture

The simulation system uses a plugin architecture for backend dispatch, making it easy
to add new generation backends without modifying core orchestration code.

### Core Components

```python
# core/backends.py

class SimulationBackend(ABC):
    """Abstract base class for simulation backends."""

    def simulate_characteristics(self) -> pd.DataFrame:
        """Generate product characteristics."""
        ...

    def simulate_metrics(self, product_characteristics: pd.DataFrame) -> pd.DataFrame:
        """Generate metrics based on characteristics."""
        ...

    @classmethod
    def get_key(cls) -> str:
        """Config key that triggers this backend (e.g., 'RULE')."""
        ...


class BackendRegistry:
    """Registry for discovering and instantiating backends."""

    @classmethod
    def register(cls, backend_cls):
        """Register a backend class."""

    @classmethod
    def detect_backend(cls, config) -> SimulationBackend:
        """Detect and instantiate appropriate backend from config."""
```

### Built-in Backends

| Backend | Config Key | Description |
|---------|------------|-------------|
| `RuleBackend` | `RULE` | Deterministic rule-based generation |
| `SynthesizerBackend` | `SYNTHESIZER` | ML-based generation using SDV |

### Backend Detection

The system automatically detects which backend to use based on config keys:

```python
# Config with RULE key -> RuleBackend
config = {"RULE": {"CHARACTERISTICS": {...}, "METRICS": {...}}}

# Config with SYNTHESIZER key -> SynthesizerBackend
config = {"SYNTHESIZER": {"CHARACTERISTICS": {...}, "METRICS": {...}}}
```

### Adding Custom Backends

To add a new backend (e.g., CTGAN, TVAE):

```python
from online_retail_simulator.core.backends import (
    BackendRegistry,
    SimulationBackend,
)

@BackendRegistry.register
class CTGANBackend(SimulationBackend):

    @classmethod
    def get_key(cls) -> str:
        return "CTGAN"

    def simulate_characteristics(self) -> pd.DataFrame:
        # Your CTGAN implementation
        ...

    def simulate_metrics(self, product_characteristics: pd.DataFrame) -> pd.DataFrame:
        # Your CTGAN implementation
        ...
```

Once registered, use it with:

```yaml
CTGAN:
  CHARACTERISTICS:
    PARAMS: {...}
  METRICS:
    PARAMS: {...}
```

## Enrichment System

### Function Registry
The system uses a unified `FunctionRegistry` class for all extensible function types:

```python
# core/registry.py
class FunctionRegistry:
    def register(self, name, func):
        """Register function with signature validation"""

    def get(self, name):
        """Retrieve registered function (lazy loads defaults)"""

    def list(self):
        """List all registered function names"""
```

Both simulation and enrichment registries use this common infrastructure.

### Built-in Impact Functions

#### Quantity Boost
```python
def quantity_boost(metrics, effect_size=0.5, enrichment_fraction=0.3,
                   enrichment_start="2024-11-15", seed=42, **kwargs):
    """Simple multiplicative increase in ordered units"""
    # Boosts ordered_units by effect_size for enriched products
    # Returns: List of modified metric dictionaries
```

#### Probability Boost
```python
def probability_boost(metrics, **kwargs):
    """Increase sale probability for treated products"""
    # Same as quantity_boost (probability reflected in quantity for existing records)
```

#### Combined Boost (Realistic)
```python
def combined_boost(metrics, effect_size=0.5, ramp_days=7, enrichment_fraction=0.3,
                   enrichment_start="2024-11-15", seed=42, **kwargs):
    """Gradual rollout with partial treatment"""
    # Realistic implementation with:
    # - Gradual effect ramp-up over ramp_days
    # - Partial product treatment (enrichment_fraction)
    # - Date-based activation (enrichment_start)
    # Returns: List of modified metric dictionaries
```

## Configuration

For complete configuration schema and parameter documentation, see the [Configuration Guide](configuration.md).

## Extension Points

### Custom Enrichment Functions
```python
def my_custom_effect(df, my_param, **kwargs):
    """Custom treatment effect implementation"""
    # Your logic here
    return modified_df

# Register for use
from online_retail_simulator.enrich import register_enrichment_function
register_enrichment_function("my_effect", my_custom_effect)
```

### Custom Synthesizers
```python
# Extend synthesizer support
class MyCustomSynthesizer:
    def fit(self, data):
        """Train on seed data"""

    def sample(self, num_rows):
        """Generate synthetic data"""
```
