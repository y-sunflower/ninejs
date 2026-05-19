import os
import io
import webbrowser
import tempfile
from typing import Any, Text, Optional
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from plotnine import ggplot

from ninejs.utils import (
    _vector_to_list,
    _get_and_sanitize_js,
    _normalize_tooltip_config,
    _normalize_geom_tooltips,
    _extract_geom_tooltips,
    _extract_panel_geom_tooltips,
)
from ninejs.const import TOOLTIP_GEOM_KINDS
from ninejs.typing import ArrayLike
from ninejs.css import css
from ninejs.javascript import javascript


MAIN_DIR: Path = Path(__file__).parent
TEMPLATE_DIR: Path = MAIN_DIR / "static"
CSS_PATH: str = os.path.join(TEMPLATE_DIR, "default.css")
JS_PARSER_PATH: str = os.path.join(TEMPLATE_DIR, "PlotParser.js")

env: Environment = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


class _InteractivePlot:
    """
    Class to convert static plotnine plots to interactive charts.
    """

    def __init__(self, fig: Figure | None = None, **savefig_kws: Any):
        """
        Initiate an `_InteractivePlot` instance to convert plotnine
        figures to interactive charts.

        Args:
            savefig_kws: Additional keyword arguments passed to `plt.savefig()`.
        """
        if fig is None:
            fig: Figure = plt.gcf()
        buf: io.StringIO = io.StringIO()

        # temporary change svg hashsalt and id for reproductibility
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
        self.svg_content = buf.getvalue()

        self.axes: list[Axes] = fig.get_axes()
        self.additional_css = ""
        self.additional_javascript = ""
        self.template = env.get_template("template.html")

        with open(CSS_PATH) as f:
            self._default_css = f.read()

        self._js_parser = _get_and_sanitize_js(
            file_path=JS_PARSER_PATH,
            after_pattern=r"class PlotSVGParser.*",
        )

    def add_tooltip(
        self,
        *,
        labels: Optional[ArrayLike] = None,
        groups: Optional[ArrayLike] = None,
        geom_tooltips: Optional[dict[str, dict[str, list]]] = None,
        tooltip_x_shift: int = 0,
        tooltip_y_shift: int = 0,
        ax: Optional[Axes] = None,
    ) -> "_InteractivePlot":
        self._tooltip_x_shift = tooltip_x_shift
        self._tooltip_y_shift = tooltip_y_shift

        if ax is None:
            ax: Axes = self.axes[0]
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

        if not hasattr(self, "axes_tooltip"):
            self.axes_tooltip: dict = dict()
        axe_idx: int = self.axes.index(ax) + 1
        axe_tooltip: dict[str, dict] = {
            f"axes_{axe_idx}": {
                "tooltip_labels": self._tooltip_labels,
                "tooltip_groups": self._tooltip_groups,
                **self._geom_tooltips,
            }
        }
        self.axes_tooltip.update(axe_tooltip)

        return self

    def _set_plot_data_json(self):
        if not hasattr(self, "_tooltip_labels"):
            self.add_tooltip()

        self.plot_data_json = {
            "tooltip_labels": self._tooltip_labels,
            "tooltip_groups": self._tooltip_groups,
            "tooltip_x_shift": self._tooltip_x_shift,
            "tooltip_y_shift": self._tooltip_y_shift,
            "axes": self.axes_tooltip,
        }

    def _set_html(self):
        self._set_plot_data_json()
        self.html: Text = self.template.render(
            default_css=self._default_css,
            additional_css=self.additional_css,
            svg=self.svg_content,
            plot_data_json=self.plot_data_json,
            additional_javascript=self.additional_javascript,
            js_parser=self._js_parser,
        )

    def add_css(self, css_content: str) -> "_InteractivePlot":
        self.additional_css += css_content
        return self

    def add_javascript(self, javascript_content: str) -> "_InteractivePlot":
        self.additional_javascript += javascript_content
        return self

    def save(self, file_path: str) -> "_InteractivePlot":
        self._set_html()

        with open(file_path, "w") as f:
            f.write(self.html)

        return self


class interactive:
    """
    Wrapper for a plotnine `ggplot` object to make it interactive.

    It automatically extracts
    tooltips and grouping information from the plot mapping if present.

    Arguments:
        gg (ggplot): The original plotnine `ggplot` object.
        kwargs (dict): Additional arguments passed to `plt.savefig()`.

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

    def __init__(self, gg: ggplot, **kwargs):
        self.gg = gg
        fig = gg.draw()
        df: Any = gg.data
        mapping = gg.mapping

        tooltip_labels = None
        tooltip_groups = None
        if df is not None:
            if "tooltip" in mapping:
                tooltip_labels = df[mapping["tooltip"]]
            if "data_id" in mapping:
                tooltip_groups = df[mapping["data_id"]]

        geom_tooltips = _extract_geom_tooltips(gg)
        panel_geom_tooltips = _extract_panel_geom_tooltips(gg)
        self.plot = _InteractivePlot(fig, **kwargs)

        if panel_geom_tooltips is None:
            self.plot = self.plot.add_tooltip(
                labels=tooltip_labels,
                groups=tooltip_groups,
                geom_tooltips=geom_tooltips,
            )
        else:
            layout = getattr(getattr(gg, "_build_objs", None), "layout", None)
            layout_axes = getattr(layout, "axs", None)

            for panel, geom_tooltips in panel_geom_tooltips.items():
                ax = (
                    layout_axes[panel - 1]
                    if layout_axes is not None
                    else self.plot.axes[panel - 1]
                )

                self.plot.add_tooltip(
                    labels=None, groups=None, geom_tooltips=geom_tooltips, ax=ax
                )

    def __add__(self, other_obj):
        if isinstance(other_obj, css):
            self.plot.add_css(other_obj.css_content)

        if isinstance(other_obj, javascript):
            self.plot.add_javascript(other_obj.javascript_content)

        elif isinstance(other_obj, save):
            self.plot.save(file_path=other_obj.file_path)
            # don't return anything when saving since it's considered
            # the last step
            return None

        elif isinstance(other_obj, to_html):
            self.plot._set_html()
            return self.plot.html

        elif isinstance(other_obj, show):
            temp_fd, temp_path = tempfile.mkstemp(suffix=".html")
            os.close(temp_fd)
            self.plot.save(temp_path)
            webbrowser.open(f"file://{temp_path}")

            return self

        return self


class save:
    """
    Utility class to specify an output HTML file for saving an
    interactive plot.

    ```python
    interactive(p) + save("output.html")
    ```
    """

    def __init__(self, file_path):
        self.file_path = file_path


class to_html:
    """
    Utility class to export an interactive plot as an HTML string.

    ```python
    html_plot: str = interactive(p) + to_html()
    ```
    """

    def __init__(self):
        pass


class show:
    """
    Open the HTML file in the default browser, or inside your editor.

    ```python
    interactive(p) + show()
    ```
    """

    def __init__(self):
        pass
