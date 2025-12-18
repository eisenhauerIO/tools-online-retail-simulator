# Online Retail Simulator - Project Context

## Project Overview

**online-retail-simulator** is a Python package for generating synthetic retail data for testing, demos, and experimentation. It simulates realistic e-commerce sales data without exposing real business information.

**Key Purpose**: Enable data scientists, product managers, educators, and developers to work with realistic retail data for ML training, A/B testing simulation, teaching, and application testing.

**Package Name**: `online_retail_simulator`
**Version**: 0.1.0
**License**: MIT
**Python Compatibility**: 3.8+

## Stack & Technologies

### Core Dependencies
- **pandas** (>=1.3.0) - Primary data structure (DataFrames)
- **pyyaml** - YAML configuration parsing
- **sdv** (>=1.0.0) - Optional ML-based synthesis (installed via `[synthesizer]` extra)

### Development Tools
- **hatch** - Environment and build management (primary workflow tool)
- **pytest** (>=7.0) - Testing framework
- **black** (>=22.0) - Code formatting (line-length: 120)
- **isort** - Import sorting (black profile)
- **flake8** (>=4.0) - Linting (max-line-length: 120)
- **pre-commit** - Git hooks for code quality

### Documentation
- **Sphinx** (>=4.0.0) with RTD theme
- **myst-parser** - Markdown support in docs
- **sphinx-autodoc-typehints** - Automatic API documentation

## Code Organization

```
online_retail_simulator/
├── __init__.py              # Public API exports
├── config_defaults.yaml     # Default configuration values
├── config_processor.py      # YAML config handling
├── simulate/                # Data generation
│   ├── simulate.py          # Main simulation entry point
│   ├── characteristics*.py  # Product characteristic generation
│   ├── metrics*.py          # Funnel metrics generation
│   └── rule_registry.py     # Custom rule registration
├── enrich/                  # A/B test enrichment simulation
│   └── enrich.py            # Enrichment logic
├── manage/                  # Job persistence and retrieval
│   └── jobs.py              # Job metadata and results storage
└── tests/                   # Test suite
    ├── test_*.py            # Unit tests
    └── test_full.py         # Integration tests
```

### Key Modules

- **simulate**: Generate baseline sales data (rule-based or ML-based)
- **enrich**: Simulate treatment effects for A/B testing scenarios
- **manage**: Handle job persistence, metadata, and result loading
- **config_processor**: Parse and validate YAML configurations

## Development Workflow

### Environment Setup

The project uses **hatch** for all development tasks. Two environments are available:

1. **default** - Full environment with all dependencies (SDV, docs, testing)
2. **light** - Minimal environment without SDV (faster, lighter)

```bash
# Prune and reset all environments
hatch env prune

# Run tests (automatically creates environment)
hatch run pytest

# Run in light environment
hatch -e light run pytest
```

### Common Commands

```bash
# Run full test suite
hatch run pytest

# Run specific test file
hatch run pytest online_retail_simulator/tests/test_full.py

# Run all demos
cd demo && hatch run python run_all_demos.py

# Build documentation
cd docs && hatch run make html

# Serve documentation locally
hatch run docs-serve  # http://localhost:8000

# Clean documentation build
hatch run docs-clean
```

## Testing & Quality Assurance

### Test Strategy

- **Unit tests**: `test_*.py` files test individual components
- **Integration test**: `test_full.py` validates end-to-end workflows
- Tests use `pytest` with `--flake8` flag for style checking
- All tests must pass before commits (enforced by pre-commit hook)

### Pre-commit Hooks

The project enforces code quality via `.pre-commit-config.yaml`:

1. **trailing-whitespace** - Remove trailing whitespace
2. **end-of-file-fixer** - Ensure newline at end of files
3. **check-yaml** - Validate YAML syntax
4. **check-added-large-files** - Prevent large file commits
5. **check-merge-conflict** - Detect merge conflict markers
6. **black** - Auto-format code (only `online_retail_simulator/*.py`)
7. **isort** - Sort imports (only `online_retail_simulator/*.py`)
8. **flake8** - Lint code (only `online_retail_simulator/*.py`)
9. **pytest-check** - Run full test suite on every commit

**Important**: Hooks only run on files in `online_retail_simulator/` (excludes `demo/`, `docs/`, etc.)

### Code Quality Standards

- **Line length**: 120 characters (black, flake8)
- **Python version**: Target Python 3.8+ compatibility
- **Import style**: isort with black profile
- **Formatting**: Always use black before committing
- **Exclusion**: `test_code_quality.py` is excluded from all formatting/linting hooks

## Project Integrity Workflow

**Before making major changes or releases**, follow the validation workflow in:
[_support/workflows/confirm-project-integrity.md](_support/workflows/confirm-project-integrity.md)

This workflow ensures:
1. Clean hatch environment
2. No uncommitted/untracked files
3. All tests pass
4. All demos run successfully
5. Documentation builds without errors
6. No duplicate content across docs

**Critical Rule**: If any step fails, STOP and ask the user before proceeding.

## Documentation Standards

### Documentation Sources

- **README.md** - Quick start, installation, key features
- **docs/** - Comprehensive user guide, API reference, design architecture
- Sphinx builds from `docs/` → `docs/_build/html/`
- Live docs: https://eisenhauerio.github.io/tools-catalog-generator/

### Key Documentation Files

- **docs/user-guide.md** - Tutorials, use cases, data schemas
- **docs/configuration.md** - All YAML parameters and options
- **docs/api_reference.md** - Auto-generated from docstrings
- **docs/design.md** - System architecture and technical design

### Content Ownership Rules

- **User stories**: Only in README and docs/user-guide.md
- **Data schemas**: Only in docs/user-guide.md (other files link to it)
- **Configuration examples**: Only in docs/configuration.md
- **Code examples**: Must match actual API in `__init__.py`

See [_support/workflows/maintain-documentation.md](_support/workflows/maintain-documentation.md) for details.

## API Design Patterns

### Public API (`__init__.py`)

The package exposes a clean, minimal API:

```python
# Main functions
simulate()              # Generate baseline data
enrich()               # Simulate enrichment impact
simulate_characteristics()
simulate_metrics()

# Job management
load_job_results()
load_job_metadata()
list_jobs()
cleanup_old_jobs()

# Registration (advanced)
register_enrichment_function()
register_enrichment_module()
register_characteristics_function()
register_metrics_function()
register_simulation_module()
```

### Configuration Pattern

All functions accept YAML configuration files or config dictionaries:

```python
# From YAML file
job = simulate("config.yaml")

# From dictionary
job = simulate({"num_days": 30, "seed": 42})
```

Default values are in `config_defaults.yaml`.

### Job Persistence

- All simulation/enrichment results are saved to `output/` directory
- Each job gets a unique ID (UUID)
- Metadata and results are stored separately
- Use `load_job_results(job)` to retrieve data
- Clean up old jobs with `cleanup_old_jobs(days=30)`

## Key Conventions

### Code Style

1. **Imports**: Use isort with black profile (groups: stdlib, third-party, first-party)
2. **Type hints**: Use where helpful, but not mandatory (Python 3.8 compatibility)
3. **Docstrings**: Required for all public functions (used by Sphinx autodoc)
4. **Function naming**: Use descriptive snake_case names
5. **Module organization**: Group related functionality in subpackages

### Testing Conventions

1. **Test file naming**: `test_<module_name>.py`
2. **Test function naming**: `test_<functionality>()`
3. **Fixtures**: Define reusable fixtures for common test data
4. **Assertions**: Use clear, descriptive assertion messages
5. **Coverage**: Aim for high coverage, especially for core simulation logic

### Configuration Conventions

1. **YAML files**: Use snake_case for keys
2. **Required fields**: Document clearly in config_processor.py
3. **Defaults**: Always provide sensible defaults in config_defaults.yaml
4. **Validation**: Validate config early and provide helpful error messages

## Important Files & Directories

### Configuration
- `config_defaults.yaml` - Default values for all config parameters
- `.flake8` - Flake8 configuration (max-line-length: 120)
- `pyproject.toml` - Package metadata, dependencies, tool configs
- `.pre-commit-config.yaml` - Git hooks configuration

### Directories
- `online_retail_simulator/` - Main package code
- `demo/` - Example scripts and usage demonstrations
- `docs/` - Sphinx documentation source
- `output/` - Generated data storage (gitignored)
- `_support/workflows/` - Project maintenance workflows
- `.claude/` - Claude Code customizations (commands, settings)

### Git & CI
- `.gitignore` - Excludes output/, build artifacts, Python cache
- `.github/` - GitHub Actions workflows (if any)
- `.gitmodules` - Git submodules configuration

## Common Tasks & How-Tos

### Adding a New Simulation Function

1. Create function in `simulate/` directory
2. Register it via `register_characteristics_function()` or `register_metrics_function()`
3. Add tests in `tests/test_*.py`
4. Update documentation in `docs/`
5. Add demo example in `demo/`

### Adding a New Enrichment Function

1. Create function in `enrich/` directory
2. Register via `register_enrichment_function()`
3. Add tests in `tests/test_enrichment.py`
4. Document in `docs/configuration.md`

### Running Specific Tests

```bash
# Single test file
hatch run pytest online_retail_simulator/tests/test_full.py -v

# Specific test function
hatch run pytest online_retail_simulator/tests/test_full.py::test_function_name -v

# With output
hatch run pytest -v -s
```

### Building & Checking Documentation

```bash
# Build docs
cd docs && hatch run make html

# Serve locally and preview
hatch run docs-serve
# Open http://localhost:8000 in browser

# Clean and rebuild
hatch run docs-clean && cd docs && hatch run make html
```

### Making a Release

1. Run full validation: `_support/workflows/confirm-project-integrity.md`
2. Update version in `pyproject.toml` and `__init__.py`
3. Update CHANGELOG (if exists)
4. Commit changes
5. Create git tag: `git tag v0.1.0`
6. Push with tags: `git push --tags`

## Gotchas & Tips

### Environment Management

- **Always use hatch**: Don't use `pip install` directly; use `hatch run` for consistency
- **Prune regularly**: Run `hatch env prune` if you encounter dependency issues
- **Light vs default**: Use `hatch -e light run` for faster testing without SDV

### SDV Dependency

- **Optional**: SDV is only required for ML-based synthesis
- **Heavy**: SDV is a large dependency; light environment excludes it
- **Import handling**: Code gracefully handles missing SDV with helpful error messages

### Testing

- **Pre-commit runs all tests**: Commits trigger full test suite (can be slow)
- **Skip hooks**: Use `git commit --no-verify` only in emergencies
- **Test isolation**: Tests should not depend on each other or external state

### Configuration

- **YAML vs dict**: Functions accept both; YAML is preferred for readability
- **Config validation**: Invalid configs fail early with clear error messages
- **Paths**: Use absolute paths or paths relative to project root in configs

### Documentation

- **Auto-generated**: API docs are built from docstrings; keep them accurate
- **Cross-references**: Use Sphinx `:ref:` and `:doc:` for internal links
- **Schema updates**: When changing data schemas, update docs/user-guide.md

### Output Directory

- **Not version controlled**: `output/` is gitignored
- **Job cleanup**: Old jobs accumulate; use `cleanup_old_jobs()` periodically
- **Paths**: Job results include absolute paths; portable across machines

## When to Ask Questions

Before making changes, ask the user if:

1. **Adding new dependencies** - Impacts environment setup and users
2. **Changing public API** - Breaking changes affect existing users
3. **Modifying data schemas** - Could break downstream workflows
4. **Updating core algorithms** - May change simulation results
5. **Restructuring code** - Large refactors need approval
6. **Changing configuration format** - Affects all YAML files

## Resources

- **Documentation**: https://eisenhauerio.github.io/tools-catalog-generator/
- **GitHub Issues**: https://github.com/eisenhauerio/tools-catalog-generator/issues
- **Hatch Docs**: https://hatch.pypa.io/
- **Sphinx Guide**: https://www.sphinx-doc.org/
