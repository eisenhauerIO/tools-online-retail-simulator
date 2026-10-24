# Online Retail Simulator

## Project overview

Generates synthetic product and sales data, with controlled treatment effects, for end-to-end
testing of causal inference pipelines. Always use Hatch as the project management and build tool.

## Development setup

- Hatch environments are defined in `pyproject.toml`: `default` (Python 3.12, full
  dependencies), `light` (minimal dependencies, used by CI), and `docs` (Sphinx).
- `pre-commit install` enables the hooks in `.pre-commit-config.yaml` (nbstripout, ruff, pytest,
  notebook execution).

## Common commands

- `hatch run test` — pytest on `online_retail_simulator/tests/`.
- `hatch run lint` — `ruff check .`
- `hatch run format` — `ruff format .`
- `hatch run docs:build` — Sphinx HTML build into `docs/build/html`.

## Architecture

Package `online_retail_simulator/`:

- `core/` — backend plugin architecture and function registry.
- `simulate/` — simulate workflow: products, product details, and metrics (rule- or
  synthesizer-based).
- `enrich/` — enrich workflow: applies enrichment treatments to metrics data.
- `quality/` — product data quality score.
- `manage/` — job management for simulation results.

Configuration defaults live in `online_retail_simulator/config_defaults.yaml`, processed by
`config_processor.py`. Design detail is in `docs/source/design.md`.

## Verification

- `hatch run test` and `hatch run lint` pass.
- CI (`.github/workflows/ci.yml`) runs `hatch run light:pytest online_retail_simulator/tests -v`.
- Notebooks under `docs/source/notebooks/` execute (pre-commit `execute-notebooks` hook).

## Key conventions

- Ruff with line length 120 and numpy docstring convention.
- Documentation structure and style: `docs/source/GUIDELINES.md`.
