uv run coverage run --source=package_name -m pytest
uv run coverage report -m
uv run coverage xml
uv run genbadge coverage -i coverage.xml
rm coverage.xml
