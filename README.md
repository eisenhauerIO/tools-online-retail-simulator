[![CI](https://github.com/eisenhauerIO/tools-catalog-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/eisenhauerIO/tools-catalog-generator/actions/workflows/ci.yml)
[![Build Documentation](https://github.com/eisenhauerIO/tools-catalog-generator/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/eisenhauerIO/tools-catalog-generator/actions/workflows/docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/eisenhauerIO/tools-catalog-generator/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# Online Retail Simulator

*Generating synthetic product and sales data for testing causal inference pipelines*

Building and validating causal inference pipelines requires realistic data—but using production datasets introduces privacy, compliance, and operational constraints.

**Online Retail Simulator** generates fully synthetic retail data for ***end-to-end testing of causal inference workflows***. It simulates products, customers, sales, and conversion funnels while preserving key statistical and behavioral patterns found in real e-commerce systems.

Unlike generic data generators, the simulator supports ***controlled treatment effects***, enabling teams to validate estimators, stress-test identifying assumptions, and compare causal models against known ground truth—before running causal analysis on production data.

## Installation

```bash
pip install online-retail-simulator
```

## Quick Start

```python
from online_retail_simulator import simulate, load_job_results

job_info = simulate("config.yaml")
results = load_job_results(job_info)

products_df = results["products"]
metrics_df = results["metrics"]
```

## Documentation

| Guide | Description |
|-------|-------------|
| [Installation](docs/installation.md) | Install and set up for development |
| [Design](docs/design.md) | System design and architecture |
| [Usage](docs/usage.md) | Getting started with basic workflow |
| [Configuration](docs/configuration.md) | All configuration options |

## License

MIT
