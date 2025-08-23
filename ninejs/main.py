import numpy as np
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from narwhals.typing import SeriesT

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from plotnine import ggplot

import os
import io
import uuid
from typing import Text

from ninejs import style

import narwhals.stable.v2 as nw
from narwhals.stable.v2.dependencies import is_numpy_array, is_into_series

import re


def _vector_to_list(vector, name="labels and groups") -> list:
    """
    Function used to easily convert various kind of iterables to
    lists in order to have standardised objects passed to javascript.

    It accepts all backend series from narwhals and common objects
    such as numpy arrays.

    Todo: test this extensively to make sure it behaves as expected.

    Args:
        vector: A valid iterable.
        name: The name passed to the error message when type is
            invalid.

    Returns:
        A list
    """
    if isinstance(vector, (list, tuple)) or is_numpy_array(vector):
        return list(vector)
    elif is_into_series(vector):
        return nw.from_native(vector, allow_series=True).to_list()
    else:
        raise ValueError(
            f"{name} must be a Series or a valid iterable (list, tuple, ndarray...)."
        )


def _get_and_sanitize_js(file_path, after_pattern):
    with open(file_path) as f:
        content = f.read()

    match = re.search(after_pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    else:
        raise ValueError(f"Could not find '{after_pattern}' in the file")


MAIN_DIR: str = Path(__file__).parent
TEMPLATE_DIR: str = MAIN_DIR / "static"
CSS_PATH: str = os.path.join(TEMPLATE_DIR, "default.css")
JS_PARSER_PATH: str = os.path.join(TEMPLATE_DIR, "PlotParser.js")

env: Environment = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


class _InteractivePlot:
    """
    Class to convert static plotnine plots to interactive charts.
    """

    def __init__(
        self,
        fig: Figure | None = None,
        **savefig_kws: dict,
    ):
        """
        Initiate an `_InteractivePlot` instance to convert plotnine
        figures to interactive charts.

        Args:
            savefig_kws: Additional keyword arguments passed to `plt.savefig()`.
        """
        if fig is None:
            fig: Figure = plt.gcf()
        buf: io.StringIO = io.StringIO()
        fig.savefig(buf, format="svg", **savefig_kws)
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
        labels: list | tuple | np.ndarray | SeriesT | None = None,
        groups: list | tuple | np.ndarray | SeriesT | None = None,
        tooltip_x_shift: int = 0,
        tooltip_y_shift: int = 0,
        ax: Axes | None = None,
    ) -> "_InteractivePlot":
        """
        Add a tooltip to the interactive plot. You can set either
        just `labels`, just `groups`, both or none.

        Args:
            labels: An iterable containing the labels for the tooltip.
                It corresponds to the text that will appear on hover.
            groups: An iterable containing the group for tooltip. It
                corresponds to how to 'group' the tooltip. The easiest
                way to understand this argument is to check the examples
                below. Also note that the use of this argument is required
                to 'connect' the legend with plot elements.
            tooltip_x_shift: Number of pixels to shift the tooltip from
                the cursor, on the x axis.
            tooltip_y_shift: Number of pixels to shift the tooltip from
                the cursor, on the y axis.
            ax: A plotnine Axes. If `None` (default), uses first Axes.

        Returns:
            self: Returns the instance to allow method chaining.

        Examples:
            ```python
            _InteractivePlot(...).add_tooltip(
                labels=["S&P500", "CAC40", "Sunflower"],
            )
            ```

            ```python
            _InteractivePlot(...).add_tooltip(
                labels=["S&P500", "CAC40", "Sunflower"],
                columns=["S&P500", "CAC40", "Sunflower"],
            )
            ```
        """
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

        if not hasattr(self, "axes_tooltip"):
            self.axes_tooltip: dict = dict()
        axe_idx: int = self.axes.index(ax) + 1
        axe_tooltip: dict[str, dict] = {
            f"axes_{axe_idx}": {
                "tooltip_labels": self._tooltip_labels,
                "tooltip_groups": self._tooltip_groups,
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
            uuid=str(uuid.uuid4()),
            default_css=self._default_css,
            additional_css=self.additional_css,
            svg=self.svg_content,
            plot_data_json=self.plot_data_json,
            additional_javascript=self.additional_javascript,
            js_parser=self._js_parser,
            favicon_path=self._favicon_path,
            document_title=self._document_title,
        )

    def as_html(self) -> str:
        """
        Retrieve the interactive plot as an HTML string.
        This can be useful to display the plot in
        environment such as marimo, or do advanced customization.

        Returns:
            A string with all the HTML of the plot.

        Examples:
            ```python
            import marimo as mo
            from ninejs import _InteractivePlot, data

            df = data.load_iris()

            html_plot = (
                _InteractivePlot(fig=fig)
                .add_tooltip(labels=df["species"])
                .as_html()
            )

            # display in marimo
            mo.iframe(html_plot)
            ```
        """
        self._set_html()
        return self.html

    def add_css(self, css_content: str) -> "_InteractivePlot":
        """
        Add CSS to the final HTML output. This function allows you to override
        default styles or add custom CSS rules.

        See the [CSS guide](../guides/css/index.md) for more info on how to work with CSS.

        Args:
            css_content: CSS rules to apply, as a string.

        Returns:
            self: Returns the instance to allow method chaining.

        Examples:
            ```python
            _InteractivePlot(...).add_css('.tooltip {"color": "red";}')
            ```

            ```python
            from ninejs import css

            _InteractivePlot(...).add_css(css.from_file("path/to/style.css"))
            ```

            ```python
            from ninejs import css

            _InteractivePlot(...).add_css(css.from_dict({".tooltip": {"color": "red";}}))
            ```

            ```python
            from ninejs import css

            _InteractivePlot(...).add_css(
                css.from_dict({".tooltip": {"color": "red";}}),
            ).add_css(
                css.from_dict({".tooltip": {"background": "blue";}}),
            )
            ```
        """
        self.additional_css += css_content
        return self

    def save(
        self,
        file_path: str,
        favicon_path: str = "https://github.com/JosephBARBIERDARNAL/static/blob/main/python-libs/plotjs/favicon.ico?raw=true",
        document_title: str = "Made with ninejs",
    ) -> "_InteractivePlot":
        """
        Save the interactive matplotlib plots to an HTML file.

        Args:
            file_path: Where to save the HTML file. If the ".html"
                extension is missing, it's added.
            favicon_path: Path to a favicon file, remote or local.
                The default is the logo of _InteractivePlot.
            document_title: String used for the page title (the title
                tag inside the head of the html document).

        Returns:
            The instance itself to allow method chaining.

        Examples:
            ```python
            _InteractivePlot(...).save("index.html")
            ```

            ```python
            _InteractivePlot(...).save("path/to/my_chart.html")
            ```
        """
        self._favicon_path = favicon_path
        self._document_title = document_title

        self._set_html()

        if not file_path.endswith(".html"):
            file_path += ".html"
        with open(file_path, "w") as f:
            f.write(self.html)

        return self


class interactive:
    """
    Wrapper for a plotnine `ggplot` object to make it interactive.

    This class converts a static `ggplot` object into an interactive
    plot by leveraging `_InteractivePlot`. It automatically extracts
    tooltips and grouping information from the plot mapping if present.

    Attributes:
        gg (ggplot): The original plotnine `ggplot` object.
        mp (_InteractivePlot): The interactive plot instance created
            from the ggplot figure.

    Example:
        ```python
        from plotnine import ggplot, aes, geom_point
        from ninejs import interactive, css, to_html

        p = ggplot(df, aes("x", "y", tooltip="label")) + geom_point()
        (
            interactive(p)
            + css(from_file="style.css")
            + to_html("chart.html")
        )
        ```
    """

    def __init__(self, gg: ggplot):
        self.gg = ggplot
        fig = gg.draw()
        df = gg.data
        mapping = gg.mapping

        if df is not None:
            if "tooltip" in mapping:
                tooltip_labels = df[mapping["tooltip"]]
            else:
                tooltip_labels = None
            if "data_id" in mapping:
                tooltip_groups = df[mapping["data_id"]]
            else:
                tooltip_groups = None

        self.mp = _InteractivePlot(fig=fig).add_tooltip(
            labels=tooltip_labels, groups=tooltip_groups
        )

    def __add__(self, other_obj):
        if isinstance(other_obj, css):
            self.mp.add_css(other_obj.css_content)
        elif isinstance(other_obj, to_html):
            self.mp.save(file_path=other_obj.file_path)

        return self


class css:
    """
    Utility class to handle CSS injection for interactive plots.

    This class provides multiple ways to load CSS: directly from a
    string, from a dictionary, or from a CSS file. It is intended to
    be combined with `interactive` plots.

    Attributes:
        css_content (str): The CSS rules to be injected.

    Example:
        ```python
        # From string
        css_obj = css(".tooltip {color: red;}")

        # From dict
        css_obj = css(from_dict={".tooltip": {"color": "blue"}})

        # From file
        css_obj = css(from_file="style.css")
        ```
    """

    def __init__(self, from_string=None, from_dict=None, from_file=None):
        if from_string is not None:
            self.css_content = from_string
        elif from_dict is not None:
            self.css_content = style.from_dict(css_dict=from_dict)
        elif from_file is not None:
            self.css_content = style.from_file(css_file=from_file)


class to_html:
    """
    Utility class to specify an output HTML file for saving an
    interactive plot.

    Attributes:
        file_path (str): Path to the output HTML file.

    Example:
        ```python
        (
            interactive(p)
            + css(from_file="style.css")
            + to_html("output.html")
        )
        ```
    """

    def __init__(self, file_path):
        self.file_path = file_path


if __name__ == "__main__":
    from plotnine import ggplot, aes, geom_point, theme_minimal
    from plotnine.data import anscombe_quartet

    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(
                x="x",
                y="y",
                color="dataset",
                tooltip="dataset",
                data_id="dataset",
            ),
        )
        + geom_point(size=7, alpha=0.5)
        + theme_minimal()
    )

    (
        interactive(gg=gg)
        + css(".tooltip{font-size: 2em;}")
        + css(from_dict={".tooltip": {"font-size": "5em"}})
        + to_html(file_path="index.html")
    )
