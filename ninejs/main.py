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

from ninejs.utils import _vector_to_list

if os.getcwd() == "/Users/josephbarbier/Desktop/ninejs":
    # for debugging
    TEMPLATE_DIR = f"{os.getcwd()}/ninejs/static"
else:
    TEMPLATE_DIR: str = Path(__file__).parent / "static"
CSS_PATH: str = os.path.join(TEMPLATE_DIR, "default.css")

env: Environment = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


class MagicPlot:
    """
    Class to convert static plotnine plots to interactive charts.
    """

    def __init__(
        self,
        **savefig_kws: dict,
    ):
        """
        Initiate an `MagicPlot` instance to convert plotnine
        figures to interactive charts.

        Args:
            savefig_kws: Additional keyword arguments passed to `plt.savefig()`.
        """
        fig: Figure = plt.gcf()
        buf: io.StringIO = io.StringIO()
        fig.savefig(buf, format="svg", **savefig_kws)
        buf.seek(0)
        self.svg_content = buf.getvalue()

        self.axes: list[Axes] = fig.get_axes()
        if len(self.axes) == 0:
            raise ValueError(
                "No Axes found in Figure. Make sure your graph is not empty."
            )

        self.additional_css = ""
        self.template = env.get_template("template.html")

        with open(CSS_PATH) as f:
            self._default_css = f.read()

    def add_tooltip(
        self,
        *,
        labels: list | tuple | np.ndarray | SeriesT | None = None,
        groups: list | tuple | np.ndarray | SeriesT | None = None,
        tooltip_x_shift: int = 10,
        tooltip_y_shift: int = -10,
        ax: Axes | None = None,
    ) -> "MagicPlot":
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
            MagicPlot(...).add_tooltip(
                labels=["S&P500", "CAC40", "Sunflower"],
            )
            ```

            ```python
            MagicPlot(...).add_tooltip(
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
        )

    def add_css(self, css_content: str) -> "MagicPlot":
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
            MagicPlot(...).add_css('.tooltip {"color": "red";}')
            ```

            ```python
            from ninejs import css

            MagicPlot(...).add_css(css.from_file("path/to/style.css"))
            ```

            ```python
            from ninejs import css

            MagicPlot(...).add_css(css.from_dict({".tooltip": {"color": "red";}}))
            ```

            ```python
            from ninejs import css

            MagicPlot(...).add_css(
                css.from_dict({".tooltip": {"color": "red";}}),
            ).add_css(
                css.from_dict({".tooltip": {"background": "blue";}}),
            )
            ```
        """
        self.additional_css += css_content
        return self

    def save(self, file_path: str) -> "MagicPlot":
        """
        Save the interactive plotnine plots to an HTML file.

        Args:
            file_path: Where to save the HTML file. If the ".html"
                extension is missing, it's added.

        Examples:
            ```python
            MagicPlot(...).save("index.html")
            ```

            ```python
            MagicPlot(...).save("path/to/my_chart.html")
            ```
        """
        self._set_html()
        if not file_path.endswith(".html"):
            file_path += ".html"
        with open(file_path, "w") as f:
            f.write(self.html)

        return self


def make_interactive(gg: ggplot, file_path: str):
    _ = gg.draw()
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

    mp = MagicPlot().add_tooltip(labels=tooltip_labels, groups=tooltip_groups)
    mp.save(file_path)
