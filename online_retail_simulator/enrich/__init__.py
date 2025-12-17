"""Enrichment module for applying treatments to sales data."""

from .enrich import enrich
from .enrichment_registry import (
    clear_enrichment_registry,
    list_enrichment_functions,
    register_enrichment_function,
    register_enrichment_module,
)

__all__ = [
    "enrich",
    "register_enrichment_function",
    "register_enrichment_module",
    "list_enrichment_functions",
    "clear_enrichment_registry",
]
