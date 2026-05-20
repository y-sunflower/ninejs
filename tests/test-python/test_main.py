import json
import re

import numpy as np
import pandas as pd
import pytest
from plotnine import (
    aes,
    facet_wrap,
    geom_area,
    geom_bar,
    geom_col,
    geom_histogram,
    geom_jitter,
    geom_line,
    geom_path,
    geom_point,
    geom_ribbon,
    geom_step,
    ggplot,
    position_fill,
    position_stack,
    theme_minimal,
)
from plotnine.data import anscombe_quartet

from ninejs.main import (
    _get_and_sanitize_js,
    _vector_to_list,
    css,
    interactive,
    save,
    to_html,
    to_iframe,
)
import ninejs


def _plot_data_from_html(html: str) -> dict:
    match = re.search(
        r'<script id="plot-data" type="application/json">\s*(.*?)\s*</script>',
        html,
        re.S,
    )
    assert match is not None
    return json.loads(match.group(1))


def _area_plot_data(position: object = "stack") -> dict:
    df = pd.DataFrame(
        {
            "x": [1, 2, 3] * 3,
            "value": [12, 18, 15, 8, 12, 10, 5, 7, 9],
            "product": ["Product A"] * 3 + ["Product B"] * 3 + ["Product C"] * 3,
        }
    )
    gg = (
        ggplot(df, aes(x="x", y="value", fill="product", tooltip="product"))
        + geom_area(position=position, alpha=0.8)
        + theme_minimal()
    )

    html = interactive(gg=gg) + to_html()
    return _plot_data_from_html(html)


def _axes_geom_tooltips(gg: ggplot, geom_kind: str) -> dict:
    html = interactive(gg=gg) + to_html()
    plot_data = _plot_data_from_html(html)
    return plot_data["axes"]["axes_1"][geom_kind]


def test_version():
    assert ninejs.__version__ == "0.0.5"


def test_vector_to_list_accepts_common_iterables():
    assert _vector_to_list(["a", "b"]) == ["a", "b"]
    assert _vector_to_list(("a", "b")) == ["a", "b"]
    assert _vector_to_list(np.array(["a", "b"])) == ["a", "b"]


def test_vector_to_list_rejects_non_iterable_values():
    with pytest.raises(ValueError, match="labels"):
        _vector_to_list(1, name="labels")


def test_get_and_sanitize_js_returns_matching_content(tmp_path):
    js_file = tmp_path / "PlotParser.js"
    js_file.write_text("const ignored = true;\nclass PlotSVGParser {}\n")

    content = _get_and_sanitize_js(js_file, r"class PlotSVGParser.*")

    assert content == "class PlotSVGParser {}\n"


def test_get_and_sanitize_js_raises_when_pattern_is_missing(tmp_path):
    js_file = tmp_path / "PlotParser.js"
    js_file.write_text("const ignored = true;\n")

    with pytest.raises(ValueError, match="Could not find"):
        _get_and_sanitize_js(js_file, r"class PlotSVGParser.*")


def test_css_wrapper_accepts_string_dict_and_file(tmp_path):
    css_file = tmp_path / "style.css"
    css_file.write_text(".tooltip { color: red; }\n")

    assert css(".tooltip { color: red; }").css_content == ".tooltip { color: red; }"
    assert css(from_dict={".tooltip": {"color": "blue"}}).css_content == (
        ".tooltip{color:blue;}"
    )
    assert css(from_file=str(css_file)).css_content == ".tooltip { color: red; }\n"


def test_save_wrapper_stores_file_path():
    default_save = save("chart.html")
    minified_save = save("chart.html", minify=True)

    assert default_save.file_path == "chart.html"
    assert default_save.minify is False
    assert minified_save.minify is True


def test_to_html_can_minify_output():
    gg = ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y")) + geom_point()
    plot = interactive(gg=gg)

    html = plot + to_html()
    minified_html = plot + to_html(minify=True)

    assert re.search(r"</style>\s+</head>", html)
    assert "</style></head>" in minified_html
    assert len(minified_html) < len(html)
    assert len(minified_html.splitlines()) < 10


def test_save_can_minify_output(tmp_path):
    gg = ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y")) + geom_point()
    html_path = tmp_path / "chart.html"

    interactive(gg=gg) + save(html_path, minify=True)

    html = html_path.read_text()
    assert "</style></head>" in html
    assert len(html.splitlines()) < 10


def test_to_iframe_exports_html_in_srcdoc():
    gg = ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y")) + geom_point()

    iframe = interactive(gg=gg) + to_iframe(height=480)

    assert iframe.startswith("<iframe ")
    assert 'srcdoc="&lt;!doctype html&gt;' in iframe
    assert 'title="ninejs interactive plot"' in iframe
    assert 'style="width:100%;height:480px;border:0;"' in iframe
    assert 'sandbox="allow-scripts"' in iframe


def test_to_iframe_escapes_attributes_and_allows_omitting_sandbox():
    iframe = to_iframe(
        width=800,
        height="75vh",
        title='A "quoted" plot',
        sandbox=None,
    ).render("<p>x</p>")

    assert 'srcdoc="&lt;p&gt;x&lt;/p&gt;"' in iframe
    assert 'title="A &quot;quoted&quot; plot"' in iframe
    assert 'style="width:800px;height:75vh;border:0;"' in iframe
    assert "sandbox=" not in iframe


def test_html_includes_parse_diagnostics():
    gg = ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y")) + geom_point()

    html = interactive(gg=gg) + to_html()

    assert "plotParser.getSvgSummary(svg, axes)" in html
    assert "plotParser.getAxesSummary(" in html
    assert "plotParser.logParseSummary(svg_summary, axes_summaries)" in html
    assert "[ninejs] parsed chart" in html
    assert "<script src=" not in html
    assert "https://cdn" not in html
    assert "sourceMappingURL" not in html
    assert "DOMPurify 3.4.5" in html
    assert "https://d3js.org v7.9.0" in html


def test_plot_data_is_embedded_without_executable_template_literal():
    df = anscombe_quartet.head(1).copy()
    df["tooltip_payload"] = ["${globalThis.NINEJS_XSS=1}`);alert(1);//"]
    gg = (
        ggplot(data=df, mapping=aes(x="x", y="y", tooltip="tooltip_payload"))
        + geom_point()
    )

    html = interactive(gg=gg) + to_html()
    plot_data = _plot_data_from_html(html)

    assert "JSON.parse(`" not in html
    assert (
        plot_data["axes"]["axes_1"]["points"]["tooltip_labels"][0]
        == "${globalThis.NINEJS_XSS=1}`);alert(1);//"
    )


def test_line_tooltips_are_grouped_per_rendered_line():
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
        )
        + geom_line(size=4, alpha=0.5)
        + theme_minimal()
    )

    html = interactive(gg=gg) + to_html()
    plot_data = _plot_data_from_html(html)

    line_tooltips = plot_data["axes"]["axes_1"]["lines"]
    assert line_tooltips["tooltip_labels"] == ["I", "II", "III", "IV"]
    assert line_tooltips["tooltip_groups"] == [0, 1, 2, 3]


@pytest.mark.parametrize("geom", [geom_path(size=2), geom_step(size=2)])
def test_line_variant_tooltips_are_grouped_per_rendered_path(geom):
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
                group="series",
                color="series",
                tooltip="label",
                data_id="series",
            ),
        )
        + geom
        + theme_minimal()
    )

    line_tooltips = _axes_geom_tooltips(gg, "lines")
    assert line_tooltips["tooltip_labels"] == ["Alpha", "Beta"]
    assert line_tooltips["tooltip_groups"] == ["A", "B"]


@pytest.mark.parametrize("geom", [geom_col(), geom_bar(stat="identity")])
def test_bar_variant_tooltips_remain_row_level(geom):
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
        + geom
        + theme_minimal()
    )

    bar_tooltips = _axes_geom_tooltips(gg, "bars")
    assert bar_tooltips["tooltip_labels"] == ["Alpha", "Beta", "Gamma"]
    assert bar_tooltips["tooltip_groups"] == ["A", "B", "C"]


def test_jitter_tooltips_remain_row_level():
    df = pd.DataFrame(
        {
            "x": [1, 1, 2, 2],
            "y": [1, 2, 2, 3],
            "label": ["Alpha", "Beta", "Gamma", "Delta"],
            "id": ["a", "b", "c", "d"],
        }
    )
    gg = (
        ggplot(df, aes(x="x", y="y", tooltip="label", data_id="id"))
        + geom_jitter(width=0.1, height=0.1, random_state=1)
        + theme_minimal()
    )

    point_tooltips = _axes_geom_tooltips(gg, "points")
    assert point_tooltips["tooltip_labels"] == ["Alpha", "Beta", "Gamma", "Delta"]
    assert point_tooltips["tooltip_groups"] == ["a", "b", "c", "d"]


def test_ribbon_tooltips_are_grouped_per_rendered_area():
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

    area_tooltips = _axes_geom_tooltips(gg, "areas")
    assert area_tooltips["tooltip_labels"] == ["Low", "High"]
    assert area_tooltips["tooltip_groups"] == ["Low", "High"]


@pytest.mark.xfail(
    reason=(
        "geom_histogram uses stat_bin, which drops original tooltip/data_id rows; "
        "bin-level tooltip semantics need a dedicated design."
    ),
    strict=True,
)
def test_histogram_tooltips_match_rendered_bins():
    df = pd.DataFrame(
        {
            "x": [1.0, 1.1, 1.2, 2.1, 2.2, 3.0],
            "label": ["one", "two", "three", "four", "five", "six"],
        }
    )
    gg = (
        ggplot(df, aes(x="x", tooltip="label"))
        + geom_histogram(bins=3)
        + theme_minimal()
    )

    bar_tooltips = _axes_geom_tooltips(gg, "bars")
    assert len(bar_tooltips["tooltip_labels"]) == 3


def test_area_tooltips_follow_default_stack_svg_order():
    plot_data = _area_plot_data()

    area_tooltips = plot_data["axes"]["axes_1"]["areas"]
    assert area_tooltips["tooltip_labels"] == ["Product A", "Product B", "Product C"]
    assert area_tooltips["tooltip_groups"] == [2, 1, 0]


def test_area_tooltips_keep_reversed_stack_order():
    plot_data = _area_plot_data(position=position_stack(reverse=True))

    area_tooltips = plot_data["axes"]["axes_1"]["areas"]
    assert area_tooltips["tooltip_labels"] == ["Product A", "Product B", "Product C"]
    assert area_tooltips["tooltip_groups"] == [0, 1, 2]


def test_area_tooltips_follow_fill_svg_order():
    plot_data = _area_plot_data(position=position_fill())

    area_tooltips = plot_data["axes"]["axes_1"]["areas"]
    assert area_tooltips["tooltip_labels"] == ["Product A", "Product B", "Product C"]
    assert area_tooltips["tooltip_groups"] == [2, 1, 0]


def test_area_tooltips_keep_identity_order():
    plot_data = _area_plot_data(position="identity")

    area_tooltips = plot_data["axes"]["axes_1"]["areas"]
    assert area_tooltips["tooltip_labels"] == ["Product A", "Product B", "Product C"]
    assert area_tooltips["tooltip_groups"] == [0, 1, 2]


def test_point_tooltips_remain_row_level():
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(
                x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset"
            ),
        )
        + geom_point(size=7, alpha=0.5)
        + theme_minimal()
    )

    html = interactive(gg=gg) + to_html()
    plot_data = _plot_data_from_html(html)

    point_tooltips = plot_data["axes"]["axes_1"]["points"]
    assert len(point_tooltips["tooltip_labels"]) == len(anscombe_quartet)
    assert point_tooltips["tooltip_labels"][:12] == ["I"] * 11 + ["II"]
    assert point_tooltips["tooltip_groups"][:12] == ["I"] * 11 + ["II"]


def test_facet():
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(x="x", y="y", color="dataset", tooltip="x"),
        )
        + geom_point()
        + facet_wrap("dataset")
    )

    html = interactive(gg) + to_html()
    plot_data = _plot_data_from_html(html)

    for axe in ["axes_1", "axes_2", "axes_3", "axes_4"]:
        assert axe in plot_data["axes"]

        points = plot_data["axes"][axe]["points"]

        assert "tooltip_labels" in points
        assert len(points["tooltip_labels"]) == 11

        assert "tooltip_groups" in points
        assert len(points["tooltip_groups"]) == 11

    dataset_I_labels = anscombe_quartet.loc[
        anscombe_quartet["dataset"] == "I", "x"
    ].tolist()

    dataset_II_labels = anscombe_quartet.loc[
        anscombe_quartet["dataset"] == "II", "x"
    ].tolist()
    assert plot_data["axes"]["axes_1"]["points"]["tooltip_labels"] == dataset_I_labels
    assert plot_data["axes"]["axes_2"]["points"]["tooltip_labels"] == dataset_II_labels
