ty:
    uv run ty check

test:
    uv run pytest

fmt:
    uv run ruff format --check .

doc:
    uv run zensical serve

examples:
    uv run docs/examples/examples.py
