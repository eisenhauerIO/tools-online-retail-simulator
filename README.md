[![CI](https://github.com/eisenhauerIO/tools-catalog-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/eisenhauerIO/tools-catalog-generator/actions/workflows/ci.yml)
[![Build Documentation](https://github.com/eisenhauerIO/tools-catalog-generator/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/eisenhauerIO/tools-catalog-generator/actions/workflows/docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/eisenhauerIO/tools-catalog-generator/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# Online Retail Simulator

*Generating synthetic product and sales data for testing causal inference pipelines*

Building and validating causal inference pipelines requires realistic data—but using production datasets introduces privacy, compliance, and operational constraints.

Online Retail Simulator generates fully synthetic retail data designed specifically for end-to-end testing of causal inference pipelines. It simulates products, customers, sales, and conversion funnels while preserving key statistical and behavioral patterns found in real e-commerce systems.

Unlike generic data generators, the simulator supports controlled treatment effects, enabling teams to validate estimation methods, stress-test assumptions, and compare causal models against known ground truth—before running experiments in production.
