"""Pytest configuration and fixtures."""

import pytest


def has_ollama() -> bool:
    """Check if Ollama server is available."""
    try:
        import urllib.request

        req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2):
            return True
    except Exception:
        return False


# Cache the result at module load time
OLLAMA_AVAILABLE = has_ollama()


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--with-llm",
        action="store_true",
        default=False,
        help="Run tests that require LLM (Ollama)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip LLM tests unless --with-llm is passed."""
    if config.getoption("--with-llm"):
        # --with-llm given: don't skip LLM tests (but still check if Ollama is available)
        return

    skip_llm = pytest.mark.skip(reason="need --with-llm option to run")
    for item in items:
        if "llm" in item.keywords:
            item.add_marker(skip_llm)
