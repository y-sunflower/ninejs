set shell := ["bash", "-cu"]

_log title:
    @echo ""
    @echo "=== {{ title }} ==="

init:
    @command -v uv >/dev/null 2>&1 || (echo 'error: uv is required. Install uv before running just init.' >&2; exit 1)
    @command -v bun >/dev/null 2>&1 || (echo 'error: bun is required. Install bun before running just init.' >&2; exit 1)

    uv sync # Python deps
    bun install # JavaScript deps

    # Chromium for tests
    uv run playwright install --with-deps chromium

    # pre-commit
    uv run prek install

test:
    @just _log "Python tests"
    uv run pytest -v

    @just _log "JavaScript tests"
    bun test

    @echo ""
    @echo "✓ All tests passed"

test-browser:
    @just _log "Browser tests"
    uv run pytest tests/test-browser/ -v

    @echo ""
    @echo "✓ Browser tests passed"

test-python:
    @just _log "Python tests"
    uv run pytest tests/test-python/ -v

    @echo ""
    @echo "✓ Python tests passed"

test-js:
    @just _log "JavaScript tests"
    bun test

    @echo ""
    @echo "✓ JavaScript tests passed"

check:
    @just _log "=== Type checking (ty) ==="
    uv run ty check

    @just _log "=== Type checking (pyrefly) ==="
    uv run pyrefly check

    @just _log "=== Ruff format check ==="
    uv run ruff format --check .

    @just _log "=== Prettier ==="
    prettier . --write

    @just _log "=== Build docs ==="
    uv run zensical build

    @just _log "✓ All checks passed"

doc:
    uv run zensical serve

examples:
    uv run docs/examples/tooltip.py
    uv run docs/examples/grouping.py
    uv run docs/examples/line_chart.py
    uv run docs/examples/bar_plot.py
    uv run docs/examples/facet.py
    uv run docs/examples/area.py
    uv run docs/examples/coal_production.py
    uv run docs/examples/choropleth.py
    uv run docs/examples/europe_co2.py

cov:
    uv run coverage run --source=ninejs -m pytest
    uv run coverage report -m
    uv run coverage xml
    uv run genbadge coverage -i coverage.xml
    rm coverage.xml
    rm .coverage
