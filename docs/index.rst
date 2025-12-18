Online Retail Simulator Documentation
=====================================

Generate synthetic retail data for testing, demos, and experimentation without exposing real business data.

.. image:: https://img.shields.io/badge/python-3.8%2B-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

Overview
--------

The Online Retail Simulator is a lightweight Python package for generating synthetic retail data for experimentation and causal inference in e-commerce contexts. It provides realistic product catalogs and daily sales transactions with configurable parameters and reproducible results.

Key Features
~~~~~~~~~~~~

* **Two simulation modes**: Rule-based (simple) and synthesizer-based (ML-powered with SDV)
* **JSON configuration-driven workflow** for easy customization
* **Deterministic output** with seed control for reproducibility
* **Realistic data patterns** across 8 product categories
* **Treatment effect simulation** for A/B testing scenarios
* **Pandas integration** with native DataFrame output

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Basic installation (rule-based generation)
   pip install -e .

   # With ML-based generation (optional)
   pip install -e ".[synthesizer]"

   # For development
   pip install -e ".[dev]"

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from online_retail_simulator import simulate

   # Generate data using config file
   sales_df = simulate("demo/simulate/config_default_simulation.yaml")
   print(f"Generated {len(sales_df)} sales records")

Run Demo
~~~~~~~~

.. code-block:: bash

   python demo/run_all_demos.py

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   use_cases
   design
   api_reference
   configuration
   examples

User Stories
------------

📊 **Data Scientists**: Generate realistic e-commerce data for ML model training without using production data.

🧪 **Product Managers**: Simulate A/B test results before launching catalog enrichment experiments.

🎓 **Educators**: Provide clean, privacy-safe datasets for teaching e-commerce analytics concepts.

🔧 **Developers**: Create synthetic data for testing e-commerce applications without production dependencies.

Getting Help
------------

* **GitHub Issues**: Report bugs or request features
* **Documentation**: Comprehensive guides and API reference
* **Examples**: Working code samples in the demo/ directory

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
