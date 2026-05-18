# Repository Guidelines

## Project Structure & Module Organization

`ninejs/` contains the package source. Core Python APIs live in `ninejs/main.py`, shared extraction helpers in `ninejs/utils.py`, constants in `ninejs/const.py`, and CSS/JavaScript wrappers in `ninejs/css.py` and `ninejs/javascript.py`. Browser-side assets are in `ninejs/static/`, including `template.html`, `default.css`, and `PlotParser.js`.

Tests live in `tests/`, with `test_main.py` covering plot interactivity and tooltip extraction and `test_css.py` covering CSS helpers. Documentation source is in `docs/`, with executable examples in `docs/examples/index.py`. Project metadata and development dependencies are defined in `pyproject.toml`; task shortcuts are in `justfile`.

## Build, Test, and Development Commands

- `uv sync` installs runtime and development dependencies.
- `just test` runs the test suite through the project recipe.
- `just fmt` checks formatting.
- `just ty` runs static type checking with `ty`.
- `just doc` can be used when working on documentation.

## Coding Style & Naming Conventions

Use Python 3.10+ syntax and 4-space indentation. Follow the existing compact helper style: small functions, explicit names, and type hints where they improve readability. Private helpers use a leading underscore, for example `_extract_geom_tooltips`. Public user-facing wrappers use lowercase class/function names matching the current API, such as `interactive`, `save`, `css`, and `to_html`.

Run Ruff formatting before submitting changes. Avoid unrelated refactors, especially in `ninejs/static/PlotParser.js`, where DOM selectors are tightly coupled to Matplotlib SVG output.

## Testing Guidelines

Use `pytest`. Name tests as `test_<behavior>()` and keep assertions tied to observable behavior, such as generated `plot_data` JSON, tooltip labels, and axes keys. Add regression tests for each supported geom or layout behavior. For plotnine changes, prefer small `anscombe_quartet` examples and parse HTML with the existing helper pattern in `tests/test_main.py`.
