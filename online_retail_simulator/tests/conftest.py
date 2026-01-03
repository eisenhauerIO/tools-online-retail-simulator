"""Pytest configuration and fixtures."""

import pytest


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--with-llm",
        action="store_true",
        default=False,
        help="Run tests that require LLM (Ollama)",
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "llm: marks tests requiring LLM (skip without --with-llm)")


def pytest_collection_modifyitems(config, items):
    """Skip LLM tests unless --with-llm is passed."""
    if config.getoption("--with-llm"):
        return

    skip_llm = pytest.mark.skip(reason="Need --with-llm option to run")
    for item in items:
        if "llm" in item.keywords:
            item.add_marker(skip_llm)
