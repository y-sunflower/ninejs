# Contributing

Thanks for taking the time to improve `ninejs`. This guide covers the local setup and the main checks to run before opening a pull request.

**Before making changes, comment on an existing issue or open a new one.**

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

Note that once you made changes, **do some manual testing too**. Update the examples from the doc with `just examples`, run `just doc` to preview the doc and make sure examples still work as expected.

## Formatting and checks

Run the repository check command before opening a pull request:

```bash
just check
```

This runs:

- Type checking
- Code formatting/linting
- Building the docs

## Documentation

Serve the documentation locally with:

```bash
just doc
```

Then open `http://localhost:8000` to preview the documentation website.
