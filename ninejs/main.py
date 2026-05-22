from __future__ import annotations

import os
import io
import webbrowser
import tempfile
from collections.abc import Iterable, Mapping
from typing import Any, overload
from pathlib import Path
import warnings

from jinja2 import Environment, FileSystemLoader, Template
import matplotlib.pyplot as plt
from matplotlib.artist import Artist
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from plotnine import ggplot

from ninejs.utils import (
    _vector_to_list,
    _get_js_bundle,
    _get_js_module_bundle,
    _normalize_tooltip_config,
    _normalize_geom_tooltips,
    _extract_geom_tooltips,
    _extract_panel_geom_tooltips,
)
from ninejs.const import TOOLTIP_GEOM_KINDS
from ninejs.typing import ArrayLike, GeomTooltips, Pathish
from ninejs.css import css
from ninejs.javascript import javascript
from ninejs.iframe import to_html, to_iframe
from ninejs.minify import _minify_html


MAIN_DIR: Path = Path(__file__).parent
TEMPLATE_DIR: Path = MAIN_DIR / "static"
CSS_PATH: str = os.path.join(TEMPLATE_DIR, "default.css")
JS_PARSER_PATH: str = os.path.join(TEMPLATE_DIR, "PlotParser.js")
JS_PARSER_MODULE_PATHS: list[Path] = [
    TEMPLATE_DIR / "PlotParserGeometry.js",
    TEMPLATE_DIR / "PlotParserHover.js",
    TEMPLATE_DIR / "PlotParserNearestHover.js",
    TEMPLATE_DIR / "PlotParser.js",
]
D3_PATH: str = os.path.join(TEMPLATE_DIR, "d3.min.js")
DOMPURIFY_PATH: str = os.path.join(TEMPLATE_DIR, "purify.min.js")

env: Environment = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


class _InteractivePlot:
    """
    Class to convert static plotnine plots to interactive charts.
    """

    def __init__(
        self,
        fig: Figure | None = None,
        *,
        hover_nearest: bool = False,
        **savefig_kws: Any,
    ) -> None:
        """
        Initialize an `_InteractivePlot` instance to convert plotnine
        figures to interactive charts.
        """
        if fig is None:
            fig = plt.gcf()
        buf: io.StringIO = io.StringIO()

        # Temporarily set SVG hashsalt and IDs for reproducibility.
        # https://github.com/y-sunflower/plotjs/issues/54
        old_svg_hashsalt = plt.rcParams["svg.hashsalt"]
        old_svg_id = plt.rcParams["svg.id"]
        try:
            plt.rcParams["svg.hashsalt"] = "svg-hashsalt"
            plt.rcParams["svg.id"] = "svg-id"
            fig.savefig(buf, format="svg", **savefig_kws)

        finally:
            plt.rcParams["svg.hashsalt"] = old_svg_hashsalt
            plt.rcParams["svg.id"] = old_svg_id

        buf.seek(0)
        self.svg_content: str = buf.getvalue()

        self.axes: list[Axes] = fig.get_axes()
        self.additional_css: str = ""
        self.additional_javascript: str = ""
        self.template: Template = env.get_template("template.html")
        self.hover_nearest: bool = hover_nearest
        self._tooltip_labels: list[object] = []
        self._tooltip_groups: list[object] = []
        self._tooltip_x_shift: int = 0
        self._tooltip_y_shift: int = 0
        self._legend_handles: list[Artist] = []
        self._legend_handles_labels: list[str] = []
        self._geom_tooltips: GeomTooltips = {
            geom_kind: _normalize_tooltip_config(None)
            for geom_kind in TOOLTIP_GEOM_KINDS
        }
        self.axes_tooltip: dict[str, dict[str, object]] = {}
        self.plot_data_json: dict[str, object] = {}
        self.html: str = ""

        with open(CSS_PATH) as f:
            self._default_css: str = f.read()
        self._dompurify: str = _get_js_bundle(DOMPURIFY_PATH)
        self._d3: str = _get_js_bundle(D3_PATH)

        self._js_parser: str = _get_js_module_bundle(JS_PARSER_MODULE_PATHS)

    def add_tooltip(
        self,
        *,
        labels: ArrayLike | None = None,
        groups: ArrayLike | None = None,
        geom_tooltips: Mapping[str, Mapping[str, Iterable[object]]] | None = None,
        tooltip_x_shift: int = 0,
        tooltip_y_shift: int = 0,
        ax: Axes | None = None,
    ) -> _InteractivePlot:
        self._tooltip_x_shift = tooltip_x_shift
        self._tooltip_y_shift = tooltip_y_shift

        if ax is None:
            ax = self.axes[0]
        self._legend_handles, self._legend_handles_labels = (
            ax.get_legend_handles_labels()
        )

        if labels is None:
            self._tooltip_labels = []
        else:
            self._tooltip_labels = _vector_to_list(labels)
            self._tooltip_labels.extend(self._legend_handles_labels)
        if groups is None:
            self._tooltip_groups = list(range(len(self._tooltip_labels)))
        else:
            self._tooltip_groups = _vector_to_list(groups)
            self._tooltip_groups.extend(self._legend_handles_labels)

        if geom_tooltips is None:
            default_tooltip_config = {
                "tooltip_labels": self._tooltip_labels,
                "tooltip_groups": self._tooltip_groups,
            }
            self._geom_tooltips = {
                geom_kind: _normalize_tooltip_config(default_tooltip_config)
                for geom_kind in TOOLTIP_GEOM_KINDS
            }
        else:
            self._geom_tooltips = _normalize_geom_tooltips(geom_tooltips)

        axe_idx: int = self.axes.index(ax) + 1
        axe_tooltip: dict[str, dict[str, object]] = {
            f"axes_{axe_idx}": {
                "tooltip_labels": self._tooltip_labels,
                "tooltip_groups": self._tooltip_groups,
                **self._geom_tooltips,
            }
        }
        self.axes_tooltip.update(axe_tooltip)

        return self

    def _set_plot_data_json(self) -> None:
        if not self.axes_tooltip:
            self.add_tooltip()

        self.plot_data_json = {
            "tooltip_labels": self._tooltip_labels,
            "tooltip_groups": self._tooltip_groups,
            "tooltip_x_shift": self._tooltip_x_shift,
            "tooltip_y_shift": self._tooltip_y_shift,
            "hover_nearest": self.hover_nearest,
            "axes": self.axes_tooltip,
        }

    def _set_html(self, *, minify: bool = False) -> None:
        self._set_plot_data_json()
        html = self.template.render(
            default_css=self._default_css,
            additional_css=self.additional_css,
            svg=self.svg_content,
            plot_data_json=self.plot_data_json,
            additional_javascript=self.additional_javascript,
            dompurify=self._dompurify,
            d3=self._d3,
            js_parser=self._js_parser,
        )
        self.html = _minify_html(html) if minify else html

    def add_css(self, css_content: str) -> _InteractivePlot:
        self.additional_css += css_content
        return self

    def add_javascript(self, javascript_content: str) -> _InteractivePlot:
        self.additional_javascript += javascript_content
        return self

    def save(self, file_path: Pathish, *, minify: bool = False) -> _InteractivePlot:
        """
        Save an interactive plot to an HTML file.

        Args:
            file_path: Path where the HTML file is written.
            minify: If `True`, remove whitespace between HTML tags before writing.
        """
        self._set_html(minify=minify)

        with open(file_path, "w") as f:
            f.write(self.html)

        return self


class interactive:
    """
    Wrapper for a plotnine `ggplot` object to make it interactive. It
    automatically extracts tooltips and grouping information from the
    plot mapping if present.

    Arguments:
        gg: The original plotnine `ggplot` object.
        hover_nearest: If `True`, show tooltips for the nearest
            configured element while the mouse is inside the plot panel.
            This builds a browser-side spatial index and samples path-like SVG
            elements, which can add noticeable load time for very large or
            complex charts.
        kwargs: Additional arguments passed to `plt.savefig()`.

    ```python
    from plotnine import ggplot, aes, geom_point
    from ninejs import interactive, css, save

    p = ggplot(df, aes("x", "y", tooltip="label")) + geom_point()
    (
        interactive(p)
        + css(from_file="style.css")
        + save("chart.html")
    )
    ```
    """

    def __init__(self, gg: ggplot, hover_nearest: bool = False, **kwargs: dict) -> None:
        self.gg: ggplot = gg
        fig = gg.draw()
        df: Any = gg.data
        mapping: Any = gg.mapping

        tooltip_labels: ArrayLike | None = None
        tooltip_groups: ArrayLike | None = None
        if df is not None and "tooltip" in mapping:
            tooltip_mapping: bool = True
            tooltip_labels = df[mapping["tooltip"]]
        else:
            tooltip_mapping: bool = False
        if df is not None and "data_id" in mapping:
            data_id_mapping: bool = True
            tooltip_groups = df[mapping["data_id"]]
        else:
            data_id_mapping: bool = False

        if not any([tooltip_mapping, data_id_mapping]):
            warnings.warn(
                "ggplot object has neither a tooltip or data_id aesthetic mapping."
            )

        geom_tooltips = _extract_geom_tooltips(gg)
        panel_geom_tooltips = _extract_panel_geom_tooltips(gg)
        self.plot = _InteractivePlot(fig, hover_nearest=hover_nearest, **kwargs)

        if panel_geom_tooltips is None:
            self.plot = self.plot.add_tooltip(
                labels=tooltip_labels,
                groups=tooltip_groups,
                geom_tooltips=geom_tooltips,
            )
        else:
            layout = getattr(getattr(gg, "_build_objs", None), "layout", None)
            layout_axes = getattr(layout, "axs", None)

            for panel, panel_tooltips in panel_geom_tooltips.items():
                ax = (
                    layout_axes[panel - 1]
                    if layout_axes is not None
                    else self.plot.axes[panel - 1]
                )

                self.plot.add_tooltip(
                    labels=None, groups=None, geom_tooltips=panel_tooltips, ax=ax
                )

    @overload
    def __add__(self, other_obj: css) -> interactive: ...

    @overload
    def __add__(self, other_obj: javascript) -> interactive: ...

    @overload
    def __add__(self, other_obj: save) -> None: ...

    @overload
    def __add__(self, other_obj: to_html) -> str: ...

    @overload
    def __add__(self, other_obj: to_iframe) -> str: ...

    @overload
    def __add__(self, other_obj: show) -> interactive: ...

    def __add__(
        self,
        other_obj: css | javascript | save | to_html | to_iframe | show,
    ) -> interactive | str | None:
        if isinstance(other_obj, css):
            self.plot.add_css(other_obj.css_content)

        elif isinstance(other_obj, javascript):
            self.plot.add_javascript(other_obj.javascript_content)

        elif isinstance(other_obj, save):
            self.plot.save(file_path=other_obj.file_path, minify=other_obj.minify)
            # don't return anything when saving since it's considered the last step
            return None

        elif isinstance(other_obj, to_html):
            self.plot._set_html(minify=other_obj.minify)
            return self.plot.html

        elif isinstance(other_obj, to_iframe):
            self.plot._set_html()
            return other_obj.render(self.plot.html)

        elif isinstance(other_obj, show):
            temp_fd, temp_path = tempfile.mkstemp(suffix=".html")
            os.close(temp_fd)
            self.plot.save(temp_path)
            webbrowser.open(f"file://{temp_path}")

            # don't return anything when showing since it's considered the last step
            return None

        return self


class save:
    """
    Utility class to save an interactive plot to an output HTML file.
    Set `minify=True` to remove whitespace between HTML tags.

    Arguments:
        file_path: Path to output file HTML file.
        minify: Whether to minify HTML output. If `True`, output will
            fit on a single line. The main use case for this is to avoid
            tracking large generated files.

    ```python
    interactive(p) + save("output.html")
    interactive(p) + save("output.html", minify=True)
    ```
    """

    def __init__(self, file_path: Pathish, *, minify: bool = False) -> None:
        self.file_path: Pathish = file_path
        self.minify: bool = minify


class show:
    """
    Open the HTML file in the default browser or inside your code editor.

    ```python
    interactive(p) + show()
    ```
    """

    def __init__(self) -> None:
        pass
