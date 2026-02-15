# Installation

## Requirements

- Python 3.10 or higher
- pip

## Install from PyPI

```bash
pip install online-retail-simulator
```

### Optional Extras

**Synthesizer mode** (ML-based data generation using SDV):

```bash
pip install online-retail-simulator[synthesizer]
```

**Cloud storage** (S3 and other cloud backends):

```bash
pip install online-retail-simulator[cloud]
```

## Install from Source

```bash
git clone https://github.com/eisenhauerIO/tools-online-retail-simulator.git
cd tools-online-retail-simulator
pip install -e ".[dev]"
```

## Verify Installation

```python
from online_retail_simulator import simulate
print("online-retail-simulator installed successfully")
```

## Development Setup

The project uses [Hatch](https://hatch.pypa.io/) for environment management.

```bash
pip install hatch
hatch env create
```

Install pre-commit hooks:

```bash
hatch run pre-commit install
```

Run tests and linting:

```bash
hatch run test
hatch run lint
```

Build the documentation:

```bash
hatch run docs:build
```
