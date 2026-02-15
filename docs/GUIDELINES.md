# Documentation Guidelines

## Docs Structure

Each page serves a distinct purpose. Topic-specific details belong in demo notebooks, not in guides.

| Page | Purpose |
|------|---------|
| `README.md` | Package positioning and quick start. Also the docs landing page via `index.md`. |
| `installation.md` | How to install, optional extras, development setup. |
| `design.md` | Architecture, extensibility, data flow. |
| `usage.md` | General workflow, backend-agnostic. Links to demos for specifics. |
| `configuration.md` | Parameter reference tables. |
| `api_reference.rst` | Auto-generated from source. Do not hand-edit. |
| Demo notebooks | Runnable deep dives with validation. |

---

## Writing Style

All documentation pages follow the tone set by `design.md`.

- Narrative prose with complete sentences. No sentence fragments or bullet-only pages.
- Succinct — every sentence earns its place. No filler, no restating the obvious.
- Structured — use headings, horizontal rules, tables, and code blocks to make pages scannable.
- Symmetric — when multiple items follow a pattern (backends, enrichment functions, steps), present them in parallel structure (same heading depth, same format, same level of detail).

---

## Text Formatting Conventions

| Category | Format | Examples |
|----------|--------|----------|
| Functions/methods | backticks | `simulate()`, `enrich()` |
| Variables/column names | backticks | `quality_score`, `ordered_units` |
| Config keys/values | backticks | `RULE`, `enrichment_fraction` |
| File names (no link) | backticks | `config.yaml`, `products.csv` |
| Classes/interfaces (with source) | markdown link | [SimulationBackend](path), [FunctionRegistry](path) |
| Files (with source) | markdown link | [simulate.py](path) |
| Design patterns | bold | **plugin architecture**, **function registry** |
| Key architectural concepts | bold | **backend dispatch**, **configuration-driven** |
| Tools/services | plain text | GitHub Actions, Ollama |
| File formats | plain text | YAML, JSON, CSV |

1. Use backticks for any code identifier that appears inline in prose
2. Use markdown links when referencing source files, classes, or interfaces that readers might want to navigate to
3. Use bold sparingly for design patterns and key concepts being introduced or emphasized
4. Keep tool and format names in plain text for readability
5. Write in narrative prose with complete sentences. Avoid semicolons and colons.

---

## Demo Notebooks

### Structure

Demo notebooks live in `docs/notebooks/` and follow this general progression:

1. **Setup** — imports and configuration
2. **Generate Data** — run simulation with a config file
3. **Inspect Output** — load and display results
4. **Apply Enrichment** — (if applicable) apply treatment effects
5. **Validate** — check output against expectations

### Sphinx integration

- Notebooks must run cleanly (`nbsphinx_execute = "always"`)
- Register new notebooks in `index.md` under the Demos toctree
