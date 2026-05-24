# Repository Guidelines

## Overall Rules

- Don't assume anything: always ask before doing something that hasn't been explicitly asked.
- Only focus on what the user asks, not what you think should be done.
- Only write code when explicitly asked to; when the user asks a question, just answer the question.
- Don't talk about Git diffs unless explicitly asked or particularly relevant.
- Prefer small or no-code solutions when they satisfy the request. If the user insists on a specific solution, follow their instructions.

## Project Structure

`ninejs/` contains the package source. `ninejs/__init__.py` exports the stable top-level API: `interactive`, `css`, `javascript`, `save`, `to_html`, `to_iframe`, and `show`.

Core plot wrapping lives in `ninejs/main.py`. It draws plotnine plots to SVG, extracts `aes()` mappings for `tooltip`, `data_id`, and `on_click`, and wires `hover_nearest` / `reverse_hover`. HTML and iframe export helpers live in `ninejs/iframe.py`; CSS and JavaScript injection wrappers live in `ninejs/css.py` and `ninejs/javascript.py`; extraction and sanitization helpers live in `ninejs/utils.py`; supported geom constants live in `ninejs/const.py`; type aliases live in `ninejs/typing.py`; HTML minification lives in `ninejs/minify.py`.

Browser-side assets are in `ninejs/static/`: `template.html`, `default.css`, `PlotParser.js`, `PlotParserGeometry.js`, `PlotParserHover.js`, `PlotParserNearestHover.js`, and vendored D3 / DOMPurify bundles. Be careful in these files: selectors are tightly coupled to Matplotlib's SVG output.

Optional bundled effects live in `ninejs/effects/`; currently `ninejs.effects.confetti` provides trusted JavaScript for the `on_click` aesthetic. Example data lives in `ninejs/data/`.

Tests live in `tests/`: `test-python/` for pytest unit tests, `test-javascript/` for Bun tests of the browser parser, `test-browser/` for Playwright-backed integration tests, and `test-integration/` for external-tool examples. Documentation source is in `docs/`, executable examples are in `docs/examples/`, rendered iframes are in `docs/iframes/`, and the LLM-facing public API summary is `docs/llms.txt`.

## Development Commands

- `just init` installs Python dependencies, JavaScript dependencies, Chromium for Playwright, and pre-commit hooks.
- `just test` runs Python tests and JavaScript tests.
- `just test-python` runs `tests/test-python/`.
- `just test-js` runs Bun tests.
- `just test-browser` runs `tests/test-browser/`.
- `just check` runs `ty`, `pyrefly`, Ruff format check, Prettier, and a docs build. Note that the Prettier step writes formatting changes.
- `just doc` serves the docs locally.
- `just examples` regenerates docs examples and `docs/iframes/`.
- `just cov` runs coverage and writes coverage badge inputs.

## API Invariants

- Public composition starts with `interactive(gg)`, then chains additions with `+`.
- Chainable additions are `css(...)` and `javascript(...)`; terminal additions are `save(...)`, `to_html(...)`, `to_iframe(...)`, and `show()`.
- `interactive(...) + save(...)` and `interactive(...) + show()` return `None`; `to_html(...)` and `to_iframe(...)` return strings.
- `css(...)` requires exactly one of a raw string, `from_dict`, or `from_file`. `javascript(...)` requires exactly one of a raw string or `from_file`.
- `on_click` values are JavaScript snippets from a data column. They are registered as generated handler IDs before being embedded in the output page.
- Tooltip HTML is sanitized with DOMPurify. Custom JavaScript is trusted code and runs directly in the generated page.
- Supported interactive geoms are points, jittered points, lines, paths, steps, bars, columns, histograms, areas, ribbons, and map polygons.

## Coding Style

Use Python 3.10+ syntax and 4-space indentation. Follow the compact helper style already used in the package: small functions, explicit names, and type hints where they improve readability. Private helpers use a leading underscore, for example `_extract_geom_tooltips`. Public user-facing wrappers use lowercase class/function names matching the current API.

Avoid unrelated refactors. When changing SVG parsing or browser behavior, update the Python tests, Bun parser tests, and Playwright tests as appropriate because regressions often only appear in one layer.
