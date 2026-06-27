"""Utilities to test tools like quarto, marimo, shiny and streamlit."""

import json
import re
from collections.abc import Sequence
from html import unescape
from html.parser import HTMLParser


EXPECTED_TOOLTIP_LABELS = ["I"] * 11 + ["II"] * 11 + ["III"] * 11 + ["IV"] * 11


class _IframeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.iframes: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "iframe":
            self.iframes.append(dict(attrs))


def extract_iframe_srcdocs(html: str) -> list[str]:
    parser = _IframeParser()
    parser.feed(html)

    srcdocs = [
        unescape(srcdoc)
        for iframe in parser.iframes
        if (srcdoc := iframe.get("srcdoc")) is not None
    ]

    if srcdocs:
        return srcdocs

    return _extract_escaped_iframe_srcdocs(html)


def assert_ninejs_iframe(
    html: str,
    *,
    expected_tooltip_groups: Sequence[int | str] | None = None,
    require_iframe_attrs: bool = True,
) -> str:
    srcdocs = extract_iframe_srcdocs(html)

    assert len(srcdocs) == 1
    if require_iframe_attrs:
        assert 'title="ninejs interactive plot"' in html
        assert 'sandbox="allow-scripts"' in html

    return assert_ninejs_srcdoc(
        srcdocs[0], expected_tooltip_groups=expected_tooltip_groups
    )


def assert_ninejs_srcdoc(
    srcdoc: str, *, expected_tooltip_groups: Sequence[int | str] | None = None
) -> str:
    assert "<!doctype html>" in srcdoc
    assert 'id="plot-container"' in srcdoc
    assert 'id="tooltip"' in srcdoc
    assert 'id="plot-data"' in srcdoc
    assert "<svg" in srcdoc
    assert "DOMPurify" in srcdoc
    assert "[ninejs] parsed chart" in srcdoc
    assert "initPlot();" in srcdoc
    assert "<script src=" not in srcdoc
    assert "https://cdn" not in srcdoc

    plot_data = _extract_plot_data(srcdoc)
    assert plot_data["hover_nearest"] is False
    assert plot_data["reverse_hover"] is False
    assert plot_data["zoomable"] is False

    points = plot_data["axes"]["axes_1"]["points"]
    assert points["tooltip_labels"] == EXPECTED_TOOLTIP_LABELS
    assert points["tooltip_groups"] == (
        list(range(44)) if expected_tooltip_groups is None else expected_tooltip_groups
    )
    assert points["click_handlers"] == []

    return srcdoc


def _extract_escaped_iframe_srcdocs(html: str) -> list[str]:
    decoded = html.encode("utf-8").decode("unicode_escape")

    return [
        unescape(match.group(2))
        for match in re.finditer(
            r"<iframe\s+[^>]*srcdoc=(['\"])(.*?)\1",
            decoded,
            re.S,
        )
    ]


def _extract_plot_data(srcdoc: str) -> dict:
    match = re.search(
        r'<script id="plot-data" type="application/json">\s*(.*?)\s*</script>',
        srcdoc,
        re.S,
    )

    assert match is not None
    return json.loads(match.group(1))
