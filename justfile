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
    uv run ty check
    uv run ruff format --check .
    prettier . --write

doc:
    uv run zensical serve

examples:
    uv run docs/examples/examples.py
