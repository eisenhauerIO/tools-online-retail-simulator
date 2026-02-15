# Software Design

*Last updated: February 2026*

## Overview

Online Retail Simulator generates fully synthetic retail data for testing causal inference pipelines. The architecture is **configuration-driven** and **plugin-based**. Generation backends, enrichment functions, and product detail generators are all pluggable. New implementations slot in through a registry system without modifying core orchestration code.

The system is organized into distinct, loosely-coupled modules:
- **Core**: Shared infrastructure including `FunctionRegistry` for extensible function registration
- **Simulation**: Core data generation logic
- **Enrichment**: Treatment effect application
- **Configuration**: Parameter processing and validation
- **Storage**: Data persistence and retrieval

Two complementary generation modes serve different use cases:
- **Rule-based**: Deterministic, interpretable patterns
- **Synthesizer-based**: ML-learned patterns from real data

Seed-based deterministic generation ensures consistent results across runs, reliable A/B testing scenarios, and debuggable data generation.

---

## Extensibility

The **plugin architecture** exists for a practical reason. Different teams may need custom generation logic, proprietary enrichment functions, or specialized synthesizers. The registry pattern lets custom implementations drop in without modifying core code.

Two patterns make this work.

**Backend plugin system**. Each generation backend implements [SimulationBackend](../online_retail_simulator/core/backends.py) and registers itself with the [BackendRegistry](../online_retail_simulator/core/backends.py). The orchestrator detects the appropriate backend from the config key (`RULE`, `SYNTHESIZER`, or any custom key) and delegates to it. To add a new backend, subclass `SimulationBackend`, implement `simulate_characteristics()` and `simulate_metrics()`, and register with `@BackendRegistry.register`.

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

**Function registry**. The [FunctionRegistry](../online_retail_simulator/core/registry.py) provides a unified registration system for simulation functions, enrichment functions, and product detail generators. Both simulation and enrichment registries use this common infrastructure.

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

Built-in backends:

| Backend | Config Key | Description |
|---------|------------|-------------|
| `RuleBackend` | `RULE` | Deterministic rule-based generation |
| `SynthesizerBackend` | `SYNTHESIZER` | ML-based generation using SDV |

---

## Data Flow

The system is **configuration-driven**. A single YAML config file selects which backend to use, and data flows through four stages.

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
│  ├── products.py                                            │
│  │   ├── products_rule_based.py                             │
│  │   └── products_synthesizer_based.py                      │
│  └── metrics.py                                             │
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

**Configure** loads and validates the YAML config, merging user settings with defaults from `config_defaults.yaml`. **Simulate** runs in two phases: first product characteristics, then metrics. The backend is auto-detected from the config key. **Enrich** optionally applies treatment effects using registered enrichment functions. **Store** persists all artifacts to a job directory.

### Quality Score

Products include a `quality_score` (0.0 - 1.0) that reflects data quality based on title, description, features, and brand. The score is calculated after product details are generated (not after characteristics, since there's no content to evaluate).

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

Quality score affects conversion probability in metrics simulation. If `quality_score` is not present (e.g., right after characteristics), a neutral default of 0.5 is used:
```python
# Maps quality_score [0,1] to multiplier [0.8, 1.2]
# Default 0.5 = multiplier 1.0 (no effect)
quality_score = product.get("quality_score", 0.5)
quality_multiplier = 0.8 + (quality_score * 0.4)
adjusted_sale_prob = sale_prob * quality_multiplier
```

### Built-in Impact Functions

| Function | Description |
|----------|-------------|
| `combined_boost` | Gradual rollout with ramp-up period and partial product treatment |
| `quantity_boost` | Simple multiplicative increase in ordered units |
| `probability_boost` | Alias for `quantity_boost` |

Custom enrichment functions can be registered at runtime:

```python
from online_retail_simulator.enrich import register_enrichment_function

def my_custom_effect(df, my_param, **kwargs):
    """Custom treatment effect implementation"""
    return modified_df

register_enrichment_function("my_effect", my_custom_effect)
```

---

## Engineering Practices

The codebase enforces quality through automated tooling. [GitHub Actions](https://github.com/features/actions) runs tests and linting on every push. [Ruff](https://docs.astral.sh/ruff/) handles fast linting and formatting. [pre-commit](https://pre-commit.com/) hooks catch issues locally.

For complete configuration schema and parameter documentation, see the [Configuration Guide](configuration.md).
