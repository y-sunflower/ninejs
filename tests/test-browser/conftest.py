import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, Page


@pytest.fixture(scope="session")
def browser():
    """Launch browser instance for all tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser: Browser):
    """Create a new page for each test."""
    context = browser.new_context()
    page = context.new_page()

    # Set viewport size for consistent testing
    page.set_viewport_size({"width": 1280, "height": 720})

    yield page

    # Cleanup
    page.close()
    context.close()


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Create temporary directory for HTML outputs."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def load_html():
    """Return a function to load HTML files in the page."""

    def _load_html(page: Page, html_path: Path):
        """Load HTML file and wait for it to be ready."""
        page.goto(f"file://{html_path.absolute()}")

        # Wait for SVG to be loaded
        page.wait_for_selector("svg", timeout=5000)

        # Wait for tooltip container to be present (it's hidden by default, so check for attached state)
        page.wait_for_selector(".tooltip", state="attached", timeout=5000)

        # Give JS a moment to finish initialization
        page.wait_for_timeout(100)

        return page

    return _load_html
