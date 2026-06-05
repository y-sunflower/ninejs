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
    bun test ./tests/test-javascript/*.test.js

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
    bun test ./tests/test-javascript/*.test.js

    @echo ""
    @echo "✓ JavaScript tests passed"

minify-js:
    uv run python scripts/minify_js.py

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
    for file in docs/examples/*.py; do \
        echo "Running $file"; \
        uv run "$file"; \
    done

cov:
    uv run coverage run --source=ninejs -m pytest -v
    uv run coverage report -m --fail-under=96
    uv run coverage xml
    uv run genbadge coverage -i coverage.xml
    rm coverage.xml
    rm .coverage

clean:
    rm -rf site/
    rm -rf .cache/
    rm -rf .pytest_cache/
    rm -rf .ruff_cache/
    rm -rf ninejs.egg-info/
