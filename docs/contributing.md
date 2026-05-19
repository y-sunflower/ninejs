# Contributing

Thanks for taking the time to improve `ninejs`. This guide covers the local setup and the main checks to run before opening a pull request.

**Before making changes, send a message in an issue or open a new one.**

## Fork and clone

Fork the repository on GitHub, then clone your fork locally:

```bash
git clone git@github.com:<your-username>/ninejs.git
cd ninejs
git remote add upstream https://github.com/y-sunflower/ninejs.git
git fetch upstream
```

Create a branch for your change:

```bash
git checkout -b <short-description>
```

## Prerequisites

Install these tools before setting up the project:

- Git
- `uv` for Python dependency management
- `bun` for JavaScript dependencies and tests
- (optional but recommended) `just` for running project tasks
- (optional but recommended) `prettier` on your `PATH`, used by the formatting check

## Install dependencies

Install Python dependencies, JavaScript dependencies, and the Chromium browser used by Playwright:

```bash
just init
```

This checks that `uv` and `bun` are installed, then runs:

```bash
uv sync
bun install
uv run playwright install --with-deps chromium
```

## Run tests

Run the full test suite:

```bash
just test
```

This runs both the Python tests and the JavaScript tests.
The Python test run includes the Playwright-backed browser tests.

To run smaller subsets:

```bash
just test-python
just test-js
just test-browser
```

Use `just test-browser` when you only want to run the browser interaction suite.

## Formatting and checks

Run the repository check command before opening a pull request:

```bash
just check
```

This runs:

- `uv run ty check`
- `uv run ruff format --check .`
- `prettier . --write`

## Documentation

Serve the documentation locally with:

```bash
just doc
```

Then open `http://localhost:8000` to preview the documentation website.
