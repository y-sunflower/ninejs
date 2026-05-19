import pytest
from ninejs import interactive, save
from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet

pytestmark = pytest.mark.browser


def test_tooltip_not_visible(page, tmp_output_dir, load_html):
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
        )
        + geom_point(size=4, alpha=0.7)
        + theme_minimal()
    )

    html_path = tmp_output_dir / "tooltip.html"
    interactive(gg) + save(html_path)

    load_html(page, html_path)

    # Tooltip should not be visible initially
    tooltip = page.locator(".tooltip")
    assert not tooltip.is_visible()

    # Hover over first point
    first_point = page.locator('svg g[id^="PathCollection"] path').first
    first_point.hover()

    # Tooltip should now be visible
    page.wait_for_selector(".tooltip[style*='display: block']", timeout=2000)
    assert tooltip.is_visible()

    # Check tooltip content
    tooltip_text = tooltip.inner_text()
    assert "I" == tooltip_text


def test_tooltip_content_changes(page, tmp_output_dir, load_html):
    """Test that tooltip content changes when hovering different points."""
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
        )
        + geom_point(size=4, alpha=0.7)
        + theme_minimal()
    )

    html_path = tmp_output_dir / "tooltip.html"
    interactive(gg) + save(html_path)

    load_html(page, html_path)

    points = page.locator('svg g[id^="PathCollection"] path')

    # Hover over first point
    points.nth(1).hover(force=True)
    page.wait_for_selector(".tooltip[style*='display: block']")
    tooltip = page.locator(".tooltip")
    print(tooltip.inner_text())
    assert "IV" == tooltip.inner_text()

    # Hover over second point
    points.nth(-1).hover(force=True)
    page.wait_for_timeout(100)  # Brief wait for update
    print(tooltip.inner_text())
    assert "IV" == tooltip.inner_text()

    # Hover over third point
    points.nth(15).hover(force=True)
    page.wait_for_timeout(100)
    print(tooltip.inner_text())
    assert "II" == tooltip.inner_text()


def test_tooltip_disappears_on_mouseout(page, tmp_output_dir, load_html):
    """Test that tooltip disappears when mouse leaves the plot area."""
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
        )
        + geom_point(size=4, alpha=0.7)
        + theme_minimal()
    )

    html_path = tmp_output_dir / "tooltip.html"
    interactive(gg) + save(html_path)

    load_html(page, html_path)

    point = page.locator('svg g[id^="PathCollection"] path').first
    point.hover()
    page.wait_for_selector(".tooltip[style*='display: block']")

    # Move mouse away from SVG
    page.mouse.move(0, 0)
    page.wait_for_timeout(100)

    # Tooltip should be hidden
    tooltip = page.locator(".tooltip")
    assert not tooltip.is_visible()
