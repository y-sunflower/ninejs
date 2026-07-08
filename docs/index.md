<br>

<img src="https://github.com/JosephBARBIERDARNAL/static/blob/main/python-libs/ninejs/image.png?raw=true" alt="ninejs logo" align="right" width="150px"/>

<div style="font-size: 1.6em">

<h1>ninejs</h1>

<div style="font-size: 0.8em">

Bringing ✨<b><i>interactivity</i></b>✨ to plotnine.

</div>

</div>

![Coverage](https://github.com/y-sunflower/ninejs/blob/main/coverage-badge.svg?raw=true)
![Python Versions](https://img.shields.io/badge/Python-3.10–3.14-blue)

`ninejs` adds interactive behavior to plotnine charts with a minimal API. You can attach tooltips, hover grouping, and on click events directly from `aes()`, then export the result as a standalone HTML plot. All of this **with just 2 lines of code**!

- Works out of the box with [Jupyter](./guide/jupyter.md), [Quarto](./guide/quarto.md), [Marimo](./guide/marimo.md), and [Shiny](./guide/shiny.md)
- Includes a built-in [preview in Positron](./guide/positron.md)
- Supports custom [CSS](./guide/css.md) and [JavaScript](./guide/javascript.md)
- Copy-pastable [self contained documentation](#tools-for-ai-and-agents) for AI and agents

## Quick start

Specify the `tooltip` and `hover_group` aesthetic mappings, and then pass your plotnine chart to `interactive()`:

```py hl_lines="9 15"
from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import interactive, save

gg = (
    ggplot(
        data=anscombe_quartet,
        mapping=aes(x="x", y="y", color="dataset", tooltip="dataset", hover_group="dataset"),
    )
    + geom_point(size=7, alpha=0.5)
    + theme_minimal()
)

interactive(gg) + save("plot.html")
```

<iframe width="100%" height="600" src="iframes/quickstart2.html" style="border:none;"></iframe>

## Installation

=== "pip"

    ```
    pip install ninejs
    ```

=== "uv"

    ```
    uv add ninejs
    ```

=== "pixi"

    ```
    pixi add ninejs
    ```

## Examples

<!-- Here we highlight the code like it's R because it looks better than python, for some reason. Do not change it. -->

=== "Linked hover"

    ```R
    map_plot = (
        ggplot()
        + geom_map(
            data=regions,
            mapping=aes(fill="region", tooltip="tooltip", hover_key="region"),
        )
        + theme_void()
    )

    bar_plot = (
        ggplot(bars, aes("reorder(region, value)", "value"))
        + geom_col(aes(fill="region", tooltip="tooltip", hover_key="region"))
        + theme_void()
    )

    plot = map_plot | bar_plot

    interactive(plot) + save("docs/iframes/linked-map-bars.html")
    ```

    <iframe width="100%" height="560" src="iframes/linked-map-bars.html" style="border:none;"></iframe>

=== "Area chart"

    ```R
    gg = (
        ggplot(df, aes(x="date", y="value", fill="group", tooltip="group"))
        + geom_area(alpha=0.8)
        + theme_minimal()
        + labs(title="Monthly Growth by Product", x="Date", y="Value", fill="Category")
        + scale_x_date(date_labels="%b")
        + theme(
            figure_size=(10, 5),
            plot_title=element_text(size=16, weight="bold"),
            axis_title=element_text(size=11),
            axis_text=element_text(size=10),
            legend_title=element_text(size=11),
            legend_text=element_text(size=10),
        )
    )

    interactive(gg) + save("docs/iframes/area-chart.html")
    ```

    <iframe width="100%" height="600" src="iframes/area-chart.html" style="border:none;"></iframe>

=== "On click"

    ```R
    anscombe_quartet["open_url"] = "window.open('https://www.ysunflower.com/')"

    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(
                x="x",
                y="y",
                color="dataset",
                tooltip="dataset",
                on_click="open_url",
            ),
        )
        + geom_point(size=7, alpha=0.7)
        + theme_minimal()
    )

    interactive(gg) + save("docs/iframes/on-click-new-window.html")
    ```

    <iframe width="100%" height="600" src="iframes/on-click-new-window.html" style="border:none;"></iframe>

=== "Bar plot"

    ```R
    gg = (
        ggplot(df, aes(x="category", y="value", tooltip="tooltip"))
        + geom_col()
        + theme_classic()
    )

    interactive(gg) + save("docs/iframes/bar.html")
    ```

    <iframe width="100%" height="600" src="iframes/bar.html" style="border:none;"></iframe>

=== "Facet"

    ```R
    gg = (
        ggplot(anscombe_quartet, aes("x", "y", tooltip="x"))
        + geom_point(color="sienna", fill="orange", size=3)
        + geom_smooth(method="lm", se=False, fullrange=True, color="steelblue", size=1)
        + facet_wrap("dataset")
        + labs(title="Anscombe’s Quartet")
        + scale_y_continuous(breaks=(4, 8, 12))
        + coord_fixed(xlim=(3, 22), ylim=(2, 14))
        + theme_tufte(base_family="Futura", base_size=16)
        + theme(
            axis_line=element_line(color="#4d4d4d"),
            axis_ticks_major=element_line(color="#00000000"),
            axis_title=element_blank(),
            panel_spacing=0.09,
        )
    )

    interactive(gg) + save("docs/iframes/facet_wrap.html")
    ```

    <iframe width="100%" height="600" src="iframes/facet_wrap.html" style="border:none;"></iframe>

=== "Advanced usage"

    ```R
    plot = (
        gg.ggplot()
        + gg.geom_rect(
            data=histogram,
            mapping=gg.aes(
                xmin="xmin",
                xmax="xmax",
                ymin="ymin",
                ymax="ymax",
                fill="rate_mid",
                tooltip="tooltip",
                hover_key="unemployment",
            ),
        )
        + gg.geom_map(
            data=df,
            mapping=gg.aes(
                fill="unemployment_rate",
                tooltip="tooltip",
                hover_key="unemployment"
            ),
            color="#e6e6e6",
            size=0.08,
        )
        + gg.theme_void(base_size=9)
        + gg.theme(figure_size=(5.5, 7.5))
    )

    (
        interactive(plot, hover_nearest=True)
        + css(
            from_dict={
                ".hovered": {"stroke": "#111", "stroke-width": "1px"},
                ".tooltip": {"font-size": "1.1em", "padding": "8px 10px"},
            }
        )
        + save("docs/iframes/map-belgium-unemployment.html")
    )
    ```

    <center><iframe width="70%" height="570" src="iframes/map-belgium-unemployment.html" style="border:none;"></iframe></center>

=== "Art"

    ```R
    goo_css = """
    svg {filter: contrast(20);}

    .point {
        filter: blur(5px);
        animation: goo 3s ease-in-out infinite alternate;
    }
    .point:nth-child(2n) {animation-duration: 4s;}
    .point:nth-child(3n) {animation-duration: 8s;}

    @keyframes goo {
        from {transform: translate(-12px, -12px) scale(1);}
        to {transform: translate(12px, 12px) scale(1.3);}
    }
    """

    interactive(gg) + css(goo_css) + save("docs/iframes/animation-art.html")
    ```

    <iframe width="100%" height="500" src="iframes/animation-art.html" style="border:none;"></iframe>

This is just a **small subset** of what's possible with `ninejs`. Check out the [gallery](./gallery/index.md) and the [guides](./guide/tooltip.md) for more.

## Tools for AI and agents

=== "llms.txt"

    A single-file overview of the ninejs API, written for AI/LLMs and coding agents. This file contains **everything** an agent needs to know to use `ninejs` properly!

    <div class="llms-actions">
      <button type="button" id="llms-view" class="llms-btn" aria-expanded="false" aria-controls="llms-preview">View</button>
      <button type="button" id="llms-copy" class="llms-btn">Copy</button>
      <a id="llms-download" class="llms-btn" href="llms.txt" download="llms.txt">Download</a>
      <span id="llms-status" class="llms-status" aria-live="polite"></span>
    </div>

    <div id="llms-preview" class="llms-preview"><code id="llms-preview-content"></code></div>

    The file is also available at this URL: [llms.txt](https://y-sunflower.github.io/ninejs/llms.txt)

=== "skill"

    A `ninejs` skill that your agents will know when to use automatically. Once installed, your agent will **automatically** know when to use the skill, or you can mention it in a prompt (inside Codex / Claude Code) using the `$skill-name` syntax:

    ```bash
    Use $ninejs to make my plotnine chart interactive.
    ```

    - Install for Claude Code:

    ```bash
    claude plugin marketplace add y-sunflower/skills && claude plugin install ninejs@y-sunflower-skills
    ```

    - Install for Codex:

    ```bash
    codex plugin marketplace add y-sunflower/skills && codex plugin add ninejs@y-sunflower-skills
    ```

## Next steps?

For more in-depth explanations and feature overviews, check out:

- [Gallery](./gallery/index.md)
- [Guides](./guide/tooltip.md)
- [API reference](./reference/interactive.md)
- [Contributing guide](./contributing.md)
