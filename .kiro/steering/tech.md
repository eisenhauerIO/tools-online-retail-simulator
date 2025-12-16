# Technology Stack

## Build System & Package Management
- **Build System**: setuptools with pyproject.toml configuration
- **Package Manager**: pip with optional dependencies support
- **Python Version**: 3.8+ (supports 3.8-3.12)

## Core Dependencies
- **pandas** (>=1.3.0) - Data manipulation and analysis
- **sdv** (>=1.0.0) - Synthetic Data Vault for ML-based generation (optional)

## Development Dependencies
- **pytest** (>=7.0) - Testing framework
- **black** (>=22.0) - Code formatting
- **flake8** (>=4.0) - Linting
- **jupyter/jupyterlab** - Notebook development
- **nbconvert** - Notebook conversion

## Installation Commands

### Development Setup
```bash
pip install -e ".[dev]"
```

### Light Installation (minimal dependencies)
```bash
pip install -e ".[light]"
```

### With Synthesizer Support
```bash
pip install -e ".[synthesizer]"
```

## Common Commands

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
```

### Linting
```bash
flake8
```

### Running Demo
```bash
python demo/example.py
```

## Architecture Patterns
- **Configuration-driven**: JSON configs control simulation behavior
- **Modular design**: Separate modules for characteristics and metrics simulation
- **Mode-based**: Rule-based vs synthesizer-based simulation modes
- **Reproducible**: Seed-based deterministic output