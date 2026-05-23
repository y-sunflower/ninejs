import pytest
import pandas as pd
from ninejs import effects, interactive, save
from ninejs.css import css
from ninejs.javascript import javascript
from plotnine import (
    aes,
    coord_cartesian,
    facet_wrap,
    geom_col,
    geom_line,
    geom_point,
    geom_ribbon,
    ggplot,
    theme_minimal,
)
from plotnine.data import anscombe_quartet

pytestmark = pytest.mark.browser


def _render_plot(
    tmp_output_dir,
    name,
    gg,
    *additions,
    minify=False,
    hover_nearest=False,
    reverse_hover=False,
):
    html_path = tmp_output_dir / f"{name}.html"
    plot = interactive(gg, hover_nearest=hover_nearest, reverse_hover=reverse_hover)
    for addition in additions:
        plot = plot + addition
    plot + save(html_path, minify=minify)
    return html_path


def _hover_and_get_tooltip(page, element):
    element.hover(force=True)
    page.wait_for_selector(".tooltip[style*='display: block']", timeout=2000)
    return page.locator(".tooltip")


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
    interactive(gg) + save(html_path, minify=True)

    load_html(page, html_path)

    # Tooltip should not be visible initially
    tooltip = page.locator(".tooltip")
    assert not tooltip.is_visible()

    # Hover over first point
    first_point = page.locator('svg g[id^="PathCollection"] .point.plot-element').first
    first_point.hover()

    # Tooltip should now be visible
    page.wait_for_selector(".tooltip[style*='display: block']", timeout=2000)
    assert tooltip.is_visible()

    # Check tooltip content
    tooltip_text = tooltip.inner_text()
    assert "I" == tooltip_text


def test_confetti_effect_can_run_on_repeated_clicks(page, tmp_output_dir, load_html):
    df = anscombe_quartet.copy()
    df["click_js"] = effects.confetti
    gg = (
        ggplot(
            data=df,
            mapping=aes(
                x="x",
                y="y",
                color="dataset",
                tooltip="dataset",
                on_click="click_js",
            ),
        )
        + geom_point(size=7, alpha=0.7)
        + theme_minimal()
    )
    page_errors = []
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))
    page.on(
        "console",
        lambda msg: page_errors.append(msg.text) if msg.type == "error" else None,
    )

    html_path = _render_plot(tmp_output_dir, "confetti-repeat-click", gg)
    load_html(page, html_path)

    first_point = page.locator("svg .point.plot-element").first
    first_point.click(force=True)
    page.wait_for_timeout(300)
    first_point.click(force=True)
    page.wait_for_timeout(1000)

    assert page_errors == []


def test_line_chart_tooltip_uses_rendered_data_lines(page, tmp_output_dir, load_html):
    df = pd.DataFrame(
        {
            "x": [1, 2, 3, 1, 2, 3],
            "y": [2, 4, 3, 1, 3, 5],
            "series": ["A"] * 3 + ["B"] * 3,
            "label": ["Alpha"] * 3 + ["Beta"] * 3,
        }
    )
    gg = (
        ggplot(
            df,
            aes(
                x="x",
                y="y",
                color="series",
                group="series",
                tooltip="label",
                data_id="series",
            ),
        )
        + geom_line(size=4)
        + theme_minimal()
    )

    html_path = _render_plot(tmp_output_dir, "line-tooltip", gg)
    load_html(page, html_path)

    lines = page.locator("svg g#axes_1 path.line.plot-element")
    assert lines.count() == 2

    tooltip_labels = []
    for i in range(lines.count()):
        lines.nth(i).dispatch_event(
            "mouseover",
            {"pageX": 200, "pageY": 160, "clientX": 200, "clientY": 160},
        )
        page.wait_for_selector(".tooltip[style*='display: block']", timeout=2000)
        tooltip_labels.append(page.locator(".tooltip").inner_text())

    assert sorted(tooltip_labels) == ["Alpha", "Beta"]


def test_bar_chart_tooltip_uses_rendered_bars(page, tmp_output_dir, load_html):
    df = pd.DataFrame(
        {
            "category": ["A", "B", "C"],
            "value": [2, 5, 3],
            "label": ["Alpha", "Beta", "Gamma"],
        }
    )
    gg = (
        ggplot(
            df,
            aes(x="category", y="value", tooltip="label", data_id="category"),
        )
        + geom_col()
        + theme_minimal()
    )

    html_path = _render_plot(tmp_output_dir, "bar-tooltip", gg)
    load_html(page, html_path)

    bars = page.locator("svg g#axes_1 path.bar.plot-element")
    assert bars.count() == 3

    tooltip = _hover_and_get_tooltip(page, bars.nth(1))
    assert tooltip.inner_text() == "Beta"


def test_area_chart_tooltip_uses_rendered_areas(page, tmp_output_dir, load_html):
    df = pd.DataFrame(
        {
            "x": [1, 2, 3, 1, 2, 3],
            "ymin": [1, 2, 1, 2, 3, 2],
            "ymax": [2, 3, 2, 4, 5, 4],
            "band": ["Low"] * 3 + ["High"] * 3,
        }
    )
    gg = (
        ggplot(
            df,
            aes(
                x="x",
                ymin="ymin",
                ymax="ymax",
                fill="band",
                tooltip="band",
                data_id="band",
            ),
        )
        + geom_ribbon(alpha=0.5)
        + theme_minimal()
    )

    html_path = _render_plot(tmp_output_dir, "area-tooltip", gg)
    load_html(page, html_path)

    areas = page.locator("svg g#axes_1 path.area.plot-element")
    assert areas.count() == 2

    areas.first.dispatch_event(
        "mouseover",
        {"pageX": 200, "pageY": 160, "clientX": 200, "clientY": 160},
    )
    page.wait_for_selector(".tooltip[style*='display: block']", timeout=2000)

    assert page.locator(".tooltip").inner_text() in {"Low", "High"}


def test_grouped_point_hover_highlights_matching_data_id(
    page, tmp_output_dir, load_html
):
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(
                x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset"
            ),
        )
        + geom_point(size=4, alpha=0.7)
        + theme_minimal()
    )

    html_path = _render_plot(tmp_output_dir, "grouped-point-hover", gg)
    load_html(page, html_path)

    first_group_point = page.locator(
        'svg g#axes_1 .point.plot-element[data-group="I"]'
    ).first
    tooltip = _hover_and_get_tooltip(page, first_group_point)

    assert tooltip.inner_text() == "I"
    assert page.locator('svg g#axes_1 .point.hovered[data-group="I"]').count() == 11
    assert (
        page.locator('svg g#axes_1 .point.not-hovered[data-group="II"]').count() == 11
    )


def test_reverse_hover_dims_matching_data_id(page, tmp_output_dir, load_html):
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(
                x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset"
            ),
        )
        + geom_point(size=4, alpha=0.7)
        + theme_minimal()
    )

    html_path = _render_plot(
        tmp_output_dir, "reverse-hover-grouped-point", gg, reverse_hover=True
    )
    load_html(page, html_path)

    first_group_point = page.locator(
        'svg g#axes_1 .point.plot-element[data-group="I"]'
    ).first
    tooltip = _hover_and_get_tooltip(page, first_group_point)

    assert tooltip.inner_text() == "I"
    assert page.locator('svg g#axes_1 .point.not-hovered[data-group="I"]').count() == 11
    assert page.locator('svg g#axes_1 .point.hovered[data-group="I"]').count() == 0
    assert page.locator('svg g#axes_1 .point.not-hovered[data-group="II"]').count() == 0


def test_faceted_chart_tooltips_are_panel_local(page, tmp_output_dir, load_html):
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(
                x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset"
            ),
        )
        + geom_point(size=4, alpha=0.7)
        + facet_wrap("dataset")
        + theme_minimal()
    )

    html_path = _render_plot(tmp_output_dir, "facet-tooltip", gg)
    load_html(page, html_path)

    panel_two_point = page.locator("svg g#axes_2 .point.plot-element").first
    tooltip = _hover_and_get_tooltip(page, panel_two_point)

    assert tooltip.inner_text() == "II"


def test_custom_css_affects_rendered_tooltip(page, tmp_output_dir, load_html):
    gg = (
        ggplot(
            data=anscombe_quartet.head(1),
            mapping=aes(x="x", y="y", tooltip="dataset"),
        )
        + geom_point(size=4)
        + theme_minimal()
    )

    html_path = _render_plot(
        tmp_output_dir,
        "custom-css-tooltip",
        gg,
        css(".tooltip { color: rgb(255, 0, 0); font-size: 24px; }"),
    )
    load_html(page, html_path)

    tooltip = _hover_and_get_tooltip(
        page, page.locator("svg g#axes_1 .point.plot-element").first
    )

    assert tooltip.evaluate("el => getComputedStyle(el).color") == "rgb(255, 0, 0)"
    assert tooltip.evaluate("el => getComputedStyle(el).fontSize") == "24px"


def test_custom_javascript_executes_after_render(page, tmp_output_dir, load_html):
    gg = (
        ggplot(
            data=anscombe_quartet.head(1),
            mapping=aes(x="x", y="y", tooltip="dataset"),
        )
        + geom_point(size=4)
        + theme_minimal()
    )

    html_path = _render_plot(
        tmp_output_dir,
        "custom-js",
        gg,
        javascript("globalThis.__ninejs_browser_test = 'executed';"),
    )
    load_html(page, html_path)

    page.wait_for_function("globalThis.__ninejs_browser_test === 'executed'")


def test_tooltip_html_is_sanitized_in_browser(page, tmp_output_dir, load_html):
    df = pd.DataFrame(
        {
            "x": [1],
            "y": [1],
            "label": [
                "<b>safe</b><script>globalThis.__ninejs_xss = true</script>"
                '<span onclick="globalThis.__ninejs_xss = true"> text</span>'
            ],
        }
    )
    gg = ggplot(df, aes(x="x", y="y", tooltip="label")) + geom_point(size=4)

    html_path = _render_plot(tmp_output_dir, "sanitized-tooltip", gg)
    load_html(page, html_path)

    tooltip = _hover_and_get_tooltip(
        page, page.locator("svg g#axes_1 .point.plot-element").first
    )

    assert tooltip.locator("b").inner_text() == "safe"
    assert tooltip.locator("script").count() == 0
    assert tooltip.locator("span").get_attribute("onclick") is None
    assert page.evaluate("globalThis.__ninejs_xss") is None


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

    points = page.locator('svg g[id^="PathCollection"] .point.plot-element')

    # Hover over first point
    points.first.hover(force=True)
    page.wait_for_selector(".tooltip[style*='display: block']")
    tooltip = page.locator(".tooltip")
    assert "I" == tooltip.inner_text()

    # Hover over second point
    points.nth(11).hover(force=True)
    page.wait_for_timeout(100)  # Brief wait for update
    assert "II" == tooltip.inner_text()

    # Hover over third point
    points.last.hover(force=True)
    page.wait_for_timeout(100)
    assert "IV" == tooltip.inner_text()


def test_hover_nearest_shows_tooltip_from_empty_panel_space(
    page, tmp_output_dir, load_html
):
    df = pd.DataFrame(
        {
            "x": [1, 10],
            "y": [1, 10],
            "label": ["Alpha", "Beta"],
        }
    )
    gg = (
        ggplot(df, aes(x="x", y="y", tooltip="label"))
        + geom_point(size=2)
        + theme_minimal()
    )

    html_path = _render_plot(
        tmp_output_dir, "nearest-empty-space", gg, hover_nearest=True
    )
    load_html(page, html_path)

    first_point = page.locator("svg g#axes_1 .point.plot-element").first
    first_point.scroll_into_view_if_needed()
    box = first_point.bounding_box()
    assert box is not None

    page.mouse.move(box["x"] + box["width"] / 2 + 24, box["y"] + box["height"] / 2)
    page.wait_for_selector(".tooltip[style*='display: block']", timeout=2000)

    assert page.locator(".tooltip").inner_text() == "Alpha"


def test_hover_nearest_ignores_clipped_points_outside_panel(
    page, tmp_output_dir, load_html
):
    df = pd.DataFrame(
        {
            "x": [-1, 5],
            "y": [5, 5],
            "label": ["Outside", "Inside"],
        }
    )
    gg = (
        ggplot(df, aes(x="x", y="y", tooltip="label"))
        + geom_point(size=4)
        + coord_cartesian(xlim=(0, 10), ylim=(0, 10))
        + theme_minimal()
    )

    html_path = _render_plot(
        tmp_output_dir, "nearest-clipped-point", gg, hover_nearest=True
    )
    load_html(page, html_path)

    hover_point = page.evaluate(
        """
        () => {
          const svg = document.querySelector("svg");
          const clipped = svg.querySelector("g#axes_1 [clip-path]");
          const clipPath = clipped.getAttribute("clip-path");
          const clipId = clipPath.match(/#([^)"']+)/)[1];
          const rect = document.getElementById(clipId).querySelector("rect");
          const point = svg.createSVGPoint();
          point.x = Number(rect.getAttribute("x")) + 5;
          point.y = Number(rect.getAttribute("y")) + Number(rect.getAttribute("height")) / 2;

          const screenPoint = point.matrixTransform(svg.getScreenCTM());
          return { x: screenPoint.x, y: screenPoint.y };
        }
        """
    )

    page.mouse.move(hover_point["x"], hover_point["y"])
    page.wait_for_selector(".tooltip[style*='display: block']", timeout=2000)

    assert page.locator(".tooltip").inner_text() == "Inside"


def test_hover_nearest_grouped_point_highlights_matching_data_id(
    page, tmp_output_dir, load_html
):
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(
                x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset"
            ),
        )
        + geom_point(size=3, alpha=0.7)
        + theme_minimal()
    )

    html_path = _render_plot(
        tmp_output_dir, "nearest-grouped-point", gg, hover_nearest=True
    )
    load_html(page, html_path)

    first_group_point = page.locator(
        'svg g#axes_1 .point.plot-element[data-group="I"]'
    ).first
    box = first_group_point.bounding_box()
    assert box is not None

    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.wait_for_selector(".tooltip[style*='display: block']", timeout=2000)

    assert page.locator(".tooltip").inner_text() == "I"
    assert page.locator('svg g#axes_1 .point.hovered[data-group="I"]').count() == 11


def test_hover_nearest_faceted_chart_is_panel_local(page, tmp_output_dir, load_html):
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(
                x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset"
            ),
        )
        + geom_point(size=3, alpha=0.7)
        + facet_wrap("dataset")
        + theme_minimal()
    )

    html_path = _render_plot(tmp_output_dir, "nearest-facet", gg, hover_nearest=True)
    load_html(page, html_path)

    panel_two_point = page.locator("svg g#axes_2 .point.plot-element").first
    box = panel_two_point.bounding_box()
    assert box is not None

    page.mouse.move(box["x"] + box["width"] / 2 + 12, box["y"] + box["height"] / 2)
    page.wait_for_selector(".tooltip[style*='display: block']", timeout=2000)

    assert page.locator(".tooltip").inner_text() == "II"


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

    point = page.locator('svg g[id^="PathCollection"] .point.plot-element').first
    point.hover()
    page.wait_for_selector(".tooltip[style*='display: block']")

    # Move mouse away from SVG
    page.mouse.move(0, 0)
    page.wait_for_timeout(100)

    # Tooltip should be hidden
    tooltip = page.locator(".tooltip")
    assert not tooltip.is_visible()
