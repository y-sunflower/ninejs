<br>

<div align="center" style="font-size: 1.6em">

<h1>ninejs</h1>

</div>

<div  align="right">

Bringing ✨<b><i>interactivity</i></b>✨ to <a href="https://plotnine.org/">plotnine</a>.

</div>

`ninejs` adds interactive behavior to plotnine charts with a minimal, composable API. You can attach **tooltips**, **hover** grouping, and other frontend interactions directly from `aes()`, then export the result as a standalone HTML plot.

## Quick start

Specify the `tooltip` and `data_id` aesthetic mappings, and then pass your plotnine chart to `interactive()`:

```py
from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import interactive, css, save

gg = (
    ggplot(
        data=anscombe_quartet,
        mapping=aes(x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset"),
    )
    + geom_point(size=7, alpha=0.5)
    + theme_minimal()
)

(
    interactive(gg)
    + css(from_dict={".tooltip": {"font-size": "3em"}})
    + save("docs/iframes/quickstart2.html")
)
```

<iframe width="800" height="600" src="iframes/quickstart2.html" style="border:none;"></iframe>

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

=== "Tooltip"

    ```py
    from plotnine import ggplot, aes, geom_point, theme_minimal
    from plotnine.data import anscombe_quartet

    from ninejs import interactive, css, save

    gg = (
        ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", tooltip="dataset"))
        + geom_point(size=7, alpha=0.5)
        + theme_minimal()
    )

    (
        interactive(gg)
        + css(".tooltip {font-size: 2em;}")
        + save("docs/iframes/point.html")
    )
    ```

    <iframe width="800" height="600" src="iframes/point.html" style="border:none;"></iframe>

=== "Grouping"

    ```py
    from plotnine import ggplot, aes, geom_point, theme_minimal
    from plotnine.data import anscombe_quartet

    from ninejs import interactive, css, save

    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset"),
        )
        + geom_point(size=7, alpha=0.5)
        + theme_minimal()
    )

    (
        interactive(gg)
        + css(from_dict={".tooltip": {"font-size": "3em"}})
        + save("docs/iframes/quickstart2.html")
    )
    ```

    <iframe width="800" height="600" src="iframes/quickstart2.html" style="border:none;"></iframe>

=== "Line chart"

    ```python
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
        )
        + geom_line(size=4, alpha=0.5)
        + theme_minimal()
    )

    (
        interactive(gg)
        + css(from_dict={".tooltip": {"font-size": "3em"}})
        + save("docs/iframes/line.html")
    )
    ```

    <iframe width="800" height="600" src="iframes/line.html" style="border:none;"></iframe>

=== "Barplot"

    ```python
    df = pd.DataFrame({"category": ["A", "B", "C"], "value": [3, 7, 5]})
    df["tooltip"] = df["category"].astype(str) + " (" + df["value"].astype(str) + ")"


    gg = (
        ggplot(df, aes(x="category", y="value", tooltip="tooltip"))
        + geom_col()
        + theme_classic()
    )

    interactive(gg) + save("docs/iframes/bar.html")
    ```

    <iframe width="800" height="600" src="iframes/bar.html" style="border:none;"></iframe>

=== "Facet"

    ```python
    plot = (
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

    interactive(plot) + save("docs/iframes/facet_wrap.html")
    ```

    <iframe width="800" height="600" src="iframes/facet_wrap.html" style="border:none;"></iframe>
