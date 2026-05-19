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
    uv run pytest -v
    bun test

test-browser:
    uv run pytest tests/test-browser/ -v

test-python:
    uv run pytest tests/test-python/ -v

test-js:
    bun test

check:
    uv run ty check # Type checking
    uv run ruff format --check . # Code format/lint
    prettier . --write # web code format
    uv run zensical build # build doc

doc:
    uv run zensical serve

examples:
    uv run docs/examples/examples.py

cov:
    uv run coverage run --source=ninejs -m pytest
    uv run coverage report -m
    uv run coverage xml
    uv run genbadge coverage -i coverage.xml
    rm coverage.xml
    rm .coverage
