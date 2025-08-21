.PHONY: all examples gallery

examples:
	quarto render docs/index.qmd
	uv run docs/guides/advanced/advanced.py
	uv run docs/guides/css/css.py
	uv run docs/guides/javascript/javascript.py

gallery:
	quarto render docs/gallery/index.qmd

coverage:
	uv run coverage run --source=plotjs -m pytest
	uv run coverage report -m
	uv run coverage xml
	uv run genbadge coverage -i coverage.xml
	rm coverage.xml

preview:
	uv run mkdocs serve

test:
	uv run pytest    # run python tests
	npm test         # run javascript tests
