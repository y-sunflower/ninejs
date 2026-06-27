import re
import json
from importlib.metadata import version
from packaging.version import Version

import pandas as pd
import pytest
from plotnine import aes, facet_wrap, geom_point, ggplot

from ninejs.main import interactive, to_html

PLOTNINE_VERSION = Version(version("plotnine"))


def _plot_data_from_html(html: str) -> dict:
    match = re.search(
        r'<script id="plot-data" type="application/json">\s*(.*?)\s*</script>',
        html,
        re.S,
    )
    assert match is not None
    return json.loads(match.group(1))


@pytest.mark.skipif(
    PLOTNINE_VERSION < Version("0.15.0"),
    reason="Fails with plotnine < 0.15.0",
)
def test_composition_tooltips_are_serialized_per_child_plot():
    left = pd.DataFrame(
        {
            "x": [1, 2],
            "y": [2, 4],
            "label": ["Alpha left", "Beta left"],
            "key": ["alpha", "beta"],
        }
    )
    right = pd.DataFrame(
        {
            "x": [1, 2],
            "y": [3, 5],
            "label": ["Alpha right", "Beta right"],
            "key": ["alpha", "beta"],
        }
    )
    p1 = ggplot(left, aes("x", "y", tooltip="label", hover_key="key")) + geom_point()
    p2 = ggplot(right, aes("x", "y", tooltip="label", hover_key="key")) + geom_point()

    html = interactive(p1 | p2) + to_html()
    plot_data = _plot_data_from_html(html)

    assert plot_data["axes"]["axes_1"]["points"]["tooltip_labels"] == [
        "Alpha left",
        "Beta left",
    ]
    assert plot_data["axes"]["axes_2"]["points"]["tooltip_labels"] == [
        "Alpha right",
        "Beta right",
    ]
    assert plot_data["axes"]["axes_1"]["points"]["hover_keys"] == ["alpha", "beta"]
    assert plot_data["axes"]["axes_2"]["points"]["hover_keys"] == ["alpha", "beta"]


@pytest.mark.skipif(
    PLOTNINE_VERSION < Version("0.15.0"),
    reason="Fails with plotnine < 0.15.0",
)
def test_composition_tooltips_follow_faceted_child_axes():
    faceted_data = pd.DataFrame(
        {
            "panel": ["left", "left", "right", "right"],
            "x": [1, 2, 1, 2],
            "y": [2, 4, 3, 5],
            "label": ["Alpha A", "Beta A", "Alpha B", "Beta B"],
            "key": ["alpha", "beta", "alpha", "beta"],
        }
    )
    solo_data = pd.DataFrame(
        {
            "x": [1, 2],
            "y": [6, 7],
            "label": ["Alpha C", "Beta C"],
            "key": ["alpha", "beta"],
        }
    )
    faceted = (
        ggplot(faceted_data, aes("x", "y", tooltip="label", hover_key="key"))
        + geom_point()
        + facet_wrap("panel")
    )
    solo = ggplot(solo_data, aes("x", "y", tooltip="label", hover_key="key")) + (
        geom_point()
    )

    html = interactive(faceted | solo) + to_html()
    plot_data = _plot_data_from_html(html)

    assert plot_data["axes"]["axes_1"]["points"]["tooltip_labels"] == [
        "Alpha A",
        "Beta A",
    ]
    assert plot_data["axes"]["axes_2"]["points"]["tooltip_labels"] == [
        "Alpha B",
        "Beta B",
    ]
    assert plot_data["axes"]["axes_3"]["points"]["tooltip_labels"] == [
        "Alpha C",
        "Beta C",
    ]


@pytest.mark.skipif(
    PLOTNINE_VERSION < Version("0.15.0"),
    reason="Fails with plotnine < 0.15.0",
)
def test_composition_preserves_hover_nearest_flag():
    df = pd.DataFrame(
        {
            "x": [1, 2],
            "y": [2, 4],
            "label": ["Alpha", "Beta"],
        }
    )
    p1 = ggplot(df, aes("x", "y", tooltip="label")) + geom_point()
    p2 = ggplot(df, aes("x", "y", tooltip="label")) + geom_point()

    html = interactive(p1 | p2, hover_nearest=True) + to_html()
    plot_data = _plot_data_from_html(html)

    assert plot_data["hover_nearest"] is True
    assert list(plot_data["axes"]) == ["axes_1", "axes_2"]


def test_interactive_rejects_non_ggplot():
    with pytest.raises(
        ValueError,
        match="interactive\\(\\) expects a valid plotnine ggplot or composition",
    ):
        interactive("not a ggplot")  # pyrefly: ignore

    with pytest.raises(ValueError):
        interactive(None)  # pyrefly: ignore
