from __future__ import annotations

import os
import io
import webbrowser
import tempfile
from copy import deepcopy
from collections.abc import Iterable, Mapping
from typing import Any, overload, Optional
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from plotnine import ggplot

# Compositions require plotnine 0.15.0, while ninejs only
# requires 0.12.0, so we need to handle this
try:
    from plotnine.composition import Compose
except ImportError:
    Compose = None  # type: ignore

from ninejs.utils import (
    _vector_to_list,
    _complete_tooltip_config,
    _get_js_bundle,
    _mapping_column,
    _normalize_geom_tooltips,
    _merge_panel_geom_tooltips,
    _extract_panel_geom_tooltips,
    _extract_click_handler_javascript,
    _inline_style_to_presentation_attrs,
)
from ninejs.typing import ArrayLike, GeomTooltips, Pathish, PlotnineChart
from ninejs.css import css
from ninejs.javascript import javascript
from ninejs.iframe import to_html, to_iframe
from ninejs.minify import _minify_html


MAIN_DIR: Path = Path(__file__).parent
TEMPLATE_DIR: Path = MAIN_DIR / "static"
CSS_PATH: Path = TEMPLATE_DIR / "default.css"
D3_PATH: Path = TEMPLATE_DIR / "d3.min.js"
DOMPURIFY_PATH: Path = TEMPLATE_DIR / "purify.min.js"
JS_PARSER_MODULE_PATHS: list[Path] = [
    TEMPLATE_DIR / "PlotParserGeometry.js",
    TEMPLATE_DIR / "PlotParserHover.js",
    TEMPLATE_DIR / "PlotParserNearestHover.js",
    TEMPLATE_DIR / "PlotParserZoom.js",
    TEMPLATE_DIR / "PlotParser.js",
    TEMPLATE_DIR / "PlotParserInit.js",
]
JS_PARSER_MIN_PATH: Path = TEMPLATE_DIR / "PlotParser.min.js"

env: Environment = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


def _is_plotnine_composition(chart: object) -> bool:
    return Compose is not None and isinstance(chart, Compose)


class _InteractivePlot:
    def __init__(
        self,
        fig: Optional[Figure],
        *,
        hover_nearest: bool,
        reverse_hover: bool,
        zoomable: bool,
        zoom_max_scale: float = 8,
        zoom_reset_duration: int = 200,
        nearest_sample_spacing: int = 12,
        nearest_max_samples: int = 48,
        **savefig_kws: Any,
    ) -> None:
        """
        Underlying private class that handles most of the work. Practical
        wrapper around `interactive()`.
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
        self.svg_content: str = _inline_style_to_presentation_attrs(buf.getvalue())

        self.zoom_max_scale: float = zoom_max_scale
        self.zoom_reset_duration: int = zoom_reset_duration
        self.nearest_sample_spacing: int = nearest_sample_spacing
        self.nearest_max_samples: int = nearest_max_samples
        self.axes: list[Axes] = fig.get_axes()
        self.additional_css: str = ""
        self.additional_javascript: str = ""
        self.template: Template = env.get_template("template.html")
        self.hover_nearest: bool = hover_nearest
        self.reverse_hover: bool = reverse_hover
        self.zoomable: bool = zoomable
        self._tooltip_labels: list[object] = []
        self._tooltip_groups: list[object] = []
        self._hover_keys: list[object] = []
        self._click_handlers: list[object] = []
        self._geom_tooltips: GeomTooltips = {}
        self.axes_tooltip: dict[str, dict[str, object]] = {}
        self.plot_data_json: dict[str, object] = {}
        self.html: str = ""

        with open(CSS_PATH, encoding="utf-8") as f:
            self._default_css: str = f.read()
        self._dompurify: str = _get_js_bundle(DOMPURIFY_PATH)
        self._d3: str = _get_js_bundle(D3_PATH)

        self._js_parser: str = _get_js_bundle(JS_PARSER_MIN_PATH)

    def add_tooltip(
        self,
        *,
        labels: Optional[ArrayLike] = None,
        groups: Optional[ArrayLike] = None,
        hover_keys: Optional[ArrayLike] = None,
        click_handlers: Optional[ArrayLike] = None,
        geom_tooltips: Optional[Mapping[str, Mapping[str, Iterable[object]]]] = None,
        ax: Optional[Axes] = None,
    ) -> _InteractivePlot:
        if ax is None:
            ax = self.axes[0]

        tooltip_config = _complete_tooltip_config(
            labels=None if labels is None else _vector_to_list(labels),
            groups=None if groups is None else _vector_to_list(groups),
            hover_keys=None if hover_keys is None else _vector_to_list(hover_keys),
            click_handlers=None
            if click_handlers is None
            else _vector_to_list(click_handlers),
        )
        self._tooltip_labels = tooltip_config["tooltip_labels"]
        self._tooltip_groups = tooltip_config["tooltip_groups"]
        self._hover_keys = tooltip_config["hover_keys"]
        self._click_handlers = tooltip_config["click_handlers"]

        if geom_tooltips is None:
            # The axes-level labels/groups/click handlers below are the
            # browser-side fallback for geom kinds without their own
            # config, so they don't need per-geom copies.
            self._geom_tooltips = {}
        else:
            self._geom_tooltips = _normalize_geom_tooltips(geom_tooltips)

        axe_idx: int = self.axes.index(ax) + 1
        axe_tooltip: dict[str, dict[str, object]] = {
            f"axes_{axe_idx}": {
                "tooltip_labels": self._tooltip_labels,
                "tooltip_groups": self._tooltip_groups,
                "hover_keys": self._hover_keys,
                "click_handlers": self._click_handlers,
                **self._geom_tooltips,
            }
        }
        self.axes_tooltip.update(axe_tooltip)

        return self

    def _set_plot_data_json(self) -> None:
        if not self.axes_tooltip:
            self.add_tooltip()

        self.plot_data_json = {
            "hover_nearest": self.hover_nearest,
            "reverse_hover": self.reverse_hover,
            "zoomable": self.zoomable,
            "zoom_max_scale": self.zoom_max_scale,
            "zoom_reset_duration": self.zoom_reset_duration,
            "nearest_sample_spacing": self.nearest_sample_spacing,
            "nearest_max_samples": self.nearest_max_samples,
            "axes": self.axes_tooltip,
        }

    def _set_html(self, *, minify: bool, extra_line: bool) -> None:
        self._set_plot_data_json()
        plot_data_json = deepcopy(self.plot_data_json)
        click_handler_javascript = _extract_click_handler_javascript(plot_data_json)
        self.plot_data_json = plot_data_json
        html = self.template.render(
            default_css=self._default_css,
            additional_css=self.additional_css,
            svg=self.svg_content,
            plot_data_json=plot_data_json,
            click_handler_javascript=click_handler_javascript,
            additional_javascript=self.additional_javascript,
            dompurify=self._dompurify,
            d3=self._d3,
            js_parser=self._js_parser,
        )
        self.html = _minify_html(html, extra_line) if minify else html

    def add_css(self, css_content: str) -> _InteractivePlot:
        self.additional_css += css_content
        return self

    def add_javascript(self, javascript_content: str) -> _InteractivePlot:
        self.additional_javascript += javascript_content
        return self

    def save(
        self,
        file_path: Pathish,
        *,
        minify: bool,
        extra_line: bool,
    ) -> _InteractivePlot:
        self._set_html(minify=minify, extra_line=extra_line)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.html)

        return self


class interactive:
    """
    Wrapper for a plotnine `ggplot` object to make it interactive. It
    automatically extracts tooltips and grouping information from the
    plot mapping if present.

    Arguments:
        gg: The original plotnine chart.
        hover_nearest: If `True`, show tooltips for the nearest
            configured element while the mouse is inside the plot panel.
            This builds a browser-side spatial index and samples path-like SVG
            elements, which can add noticeable load time for very large or
            complex charts.
        reverse_hover: If `True`, dim the hovered element group instead of
            dimming the non-hovered elements.
        zoomable: If `True`, allow the reader to zoom and pan the chart with the
            mouse wheel and drag. This is a visual magnification of the whole
            plot (data, axes, ticks, and labels scale together); it does not
            rescale the data against fixed axes. **Double-click resets the view**.
        zoom_max_scale: Maximum zoom-in factor when `zoomable=True`. Readers
            can magnify the chart up to this many times its original size;
            zooming out below the original size is not possible. Has no
            effect when `zoomable=False`.
        zoom_reset_duration: Duration, in milliseconds, of the animation that
            returns the chart to its original view when the reader
            double-clicks a zoomed chart. Set to `0` to reset instantly. Has
            no effect when `zoomable=False`.
        width: Width of the iframe representation used in environments like
            Quarto, Jupyter, and Positron. This does not affect saved HTML files.
        height: Height of the iframe representation used in environments like
            Quarto, Jupyter, and Positron. This does not affect saved HTML files.
        nearest_max_samples: Maximum number of anchor points sampled per
            path-like element for the `hover_nearest` spatial index. Caps the
            load-time cost of very long or complex paths; past the cap,
            anchors spread farther apart than `nearest_sample_spacing`, so
            snapping precision on long lines degrades. Increase it if
            tooltips snap to the wrong line on dense charts. Has no effect
            when `hover_nearest=False`.
        nearest_sample_spacing: Distance, in SVG units, between the anchor
            points sampled along path-like elements (lines, areas, ribbons)
            for the `hover_nearest` spatial index. Smaller values make
            tooltip snapping follow curves more accurately but increase the
            index build time on load. Has no effect when
            `hover_nearest=False`.
        kwargs: Additional arguments passed to `matplotlib.pyplot.savefig()`.

    ```python
    from plotnine import ggplot, aes, geom_point
    from ninejs import interactive, css, save

    p = ggplot(df, aes("x", "y", tooltip="label")) + geom_point()

    (
        interactive(p)
        + css(from_file="style.css")
        + save("chart.html")
    )

    interactive(p, width=600, height=400)
    ```
    """

    def __init__(
        self,
        gg: PlotnineChart,
        *,
        hover_nearest: bool = False,
        reverse_hover: bool = False,
        zoomable: bool = False,
        zoom_max_scale: float = 8,
        zoom_reset_duration: int = 200,
        width: Optional[int | str] = "100%",
        height: Optional[int | str] = None,
        nearest_sample_spacing: int = 12,
        nearest_max_samples: int = 48,
        **kwargs: Any,
    ) -> None:
        if not isinstance(gg, ggplot) and not _is_plotnine_composition(gg):
            raise ValueError(
                "interactive() expects a valid plotnine ggplot or composition "
                f"object, not: {type(gg)}"
            )

        # Need to check if the Figure has already been
        # drawn to avoid drawing all Artists twice
        # https://github.com/y-sunflower/ninejs/issues/73
        fig = getattr(gg, "figure", None)
        if fig is None:
            fig = gg.draw()
            plt.close()

        self.plot = _InteractivePlot(
            fig,
            hover_nearest=hover_nearest,
            reverse_hover=reverse_hover,
            zoomable=zoomable,
            zoom_max_scale=zoom_max_scale,
            zoom_reset_duration=zoom_reset_duration,
            nearest_sample_spacing=nearest_sample_spacing,
            nearest_max_samples=nearest_max_samples,
            **kwargs,
        )
        self.fig = fig
        self._set_width_and_height(width, height)

        # Composition are plotnine charts made using
        # arithmetic operators and are a slightly different
        # kind of objects that we need to "parse".
        if _is_plotnine_composition(gg):
            self._add_composition_tooltips(gg)
        else:
            assert isinstance(gg, ggplot)
            self._add_ggplot_tooltips(gg)

    def _add_ggplot_tooltips(self, gg: ggplot) -> None:
        df: Any = gg.data
        mapping: Any = gg.mapping

        tooltip_labels = _mapping_column(df, mapping, "tooltip")
        tooltip_groups = _mapping_column(df, mapping, "hover_group")
        if tooltip_groups is None:
            tooltip_groups = _mapping_column(df, mapping, "data_id")
        hover_keys = _mapping_column(df, mapping, "hover_key")
        click_handlers = _mapping_column(df, mapping, "on_click")

        panel_geom_tooltips = _extract_panel_geom_tooltips(gg)
        geom_tooltips = _merge_panel_geom_tooltips(panel_geom_tooltips)

        if panel_geom_tooltips is None:
            self.plot = self.plot.add_tooltip(
                labels=tooltip_labels,
                groups=tooltip_groups,
                hover_keys=hover_keys,
                click_handlers=click_handlers,
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

    def _add_composition_tooltips(self, gg: PlotnineChart) -> None:
        plotspecs = getattr(gg, "plotspecs", None)
        if plotspecs is None:
            return

        for plotspec in plotspecs:
            plot = getattr(plotspec, "plot", None)
            if not isinstance(plot, ggplot):
                continue

            panel_geom_tooltips = _extract_panel_geom_tooltips(plot)
            if panel_geom_tooltips is None:
                continue

            layout = getattr(getattr(plot, "_build_objs", None), "layout", None)
            layout_axes = getattr(layout, "axs", None)

            for panel, panel_tooltips in panel_geom_tooltips.items():
                if layout_axes is None:
                    ax = self.plot.axes[panel - 1]
                else:
                    ax = layout_axes[panel - 1]

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
    def __add__(self, other_obj: show) -> None: ...

    def __add__(
        self,
        other_obj: css | javascript | save | to_html | to_iframe | show,
    ) -> Optional[interactive | str]:
        # add CSS
        if isinstance(other_obj, css):
            self.plot.add_css(other_obj.css_content)

        # add javascript
        elif isinstance(other_obj, javascript):
            self.plot.add_javascript(other_obj.javascript_content)

        # save
        elif isinstance(other_obj, save):
            self.plot.save(
                file_path=other_obj.file_path,
                minify=other_obj.minify,
                extra_line=other_obj.extra_line,
            )

            # don't return anything when saving since it's considered the last step
            return None

        # to HTML
        elif isinstance(other_obj, to_html):
            self.plot._set_html(
                minify=other_obj.minify, extra_line=other_obj.extra_line
            )
            return self.plot.html

        # to iframe
        elif isinstance(other_obj, to_iframe):
            self.plot._set_html(minify=False, extra_line=False)
            return other_obj.render(self.plot.html)

        # show
        elif isinstance(other_obj, show):
            temp_fd, temp_path = tempfile.mkstemp(suffix=".html")
            os.close(temp_fd)
            self.plot.save(temp_path, minify=True, extra_line=True)
            webbrowser.open(f"file://{temp_path}")

            # don't return anything when showing since it's considered the last step
            return None

        return self

    def _repr_html_(self) -> str:
        """
        Defines what should be printed in an IPython-like environment?
        This is what is used in Jupyter notebooks, Quarto, Positron, etc.
        """
        self.plot._set_html(minify=True, extra_line=True)
        return to_iframe(width=self.width, height=self.height).render(self.plot.html)

    def _set_width_and_height(self, width, height):
        if width is None:
            self.width = "100%"
        else:
            self.width = width

        if height is None:
            self.height = int(self.fig.get_figheight() * 96) + 16
        else:
            self.height = height


class save:
    """
    Utility class to save an interactive plot to an output HTML file.
    Set `minify=True` to remove whitespace between HTML tags.

    Arguments:
        file_path: Path to the output HTML file.
        minify: Whether to minify HTML output. If `True`, whitespace is
            collapsed outside `<script>` blocks; script content is kept
            verbatim. The main use case for this is to avoid tracking
            large generated files.
        extra_line: Whether to append a trailing newline when `minify` is
            `True`. This is mostly useful when you track your exported HTML
            file and use hooks that require a trailing newline.

    ```python
    from ninejs import interactive, save

    interactive(p) + save("output.html")
    interactive(p) + save("output.html", minify=False, extra_line=False)
    ```
    """

    def __init__(
        self,
        file_path: Pathish,
        *,
        minify: bool = True,
        extra_line: bool = True,
    ) -> None:
        self.file_path: Pathish = file_path
        self.minify: bool = minify
        self.extra_line: bool = extra_line


class show:
    """
    Open the HTML file in the default browser or inside your code editor.

    ```python
    from ninejs import interactive, show

    interactive(p) + show()
    ```
    """

    def __init__(self) -> None:
        pass
