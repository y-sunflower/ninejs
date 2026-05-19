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
    assert "I" in tooltip_text
