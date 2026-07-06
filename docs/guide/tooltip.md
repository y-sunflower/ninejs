`ninejs` lets you easily customize the tooltip, which appears when hovering over an element, using HTML and CSS.

## Default tooltip style

By default, a tooltip looks like this:

```py
import polars as pl
from plotnine import (
    ggplot,
    aes,
    geom_point,
    labs,
    facet_wrap,
    theme_minimal,
    theme,
    element_text,
    scale_fill_manual,
)
from ninejs import interactive, save, css

df = pl.read_csv(
    "https://github.com/y-sunflower/plotjs/blob/main/plotjs/data/titanic.csv?raw=true"
).with_columns(
    pl.when(pl.col("Survived") == 1)
    .then(pl.lit("Survived"))
    .otherwise(pl.lit("Did Not Survive"))
    .alias("Survival Status")
)

gg = (
    ggplot(df, aes(x="Age", y="Fare", fill="Survival Status", tooltip="Name"))
    + geom_point(size=8, alpha=0.5, show_legend=False)
    + facet_wrap("Survival Status")
    + scale_fill_manual(values={"Survived": "#4C78A8", "Did Not Survive": "#F58518"})
    + labs(x="Age", y="Fare")
    + theme_minimal()
    + theme(
        strip_text=element_text(weight="bold", size=12),
        plot_title=element_text(weight="bold", size=16),
    )
)

interactive(gg) + save("docs/iframes/tooltip-default.html")
```

<iframe width="100%" height="600" src="../iframes/tooltip-default.html" style="border:none;"></iframe>

## Change background color and text color

We can make it look better with **CSS**. If you're completely unfamiliar with CSS, check out [this other guide](css.md).

```py
(
    interactive(gg)
    + css(".tooltip {background-color: #FFC300; color: #421173;}")
    + save("docs/iframes/tooltip-custom-css.html")
)
```

<iframe width="100%" height="600" src="../iframes/tooltip-custom-css.html" style="border:none;"></iframe>

## Make the text bigger

We can make the text bigger too:

```py
(
    interactive(gg)
    + css(
        from_dict={
            ".tooltip": {
                "background-color": "#FFC300",
                "color": "#421173",
                "font-size": "1.5em",
            }
        }
    )
    + save("docs/iframes/tooltip-custom-css2.html")
)
```

<iframe width="100%" height="600" src="../iframes/tooltip-custom-css2.html" style="border:none;"></iframe>

!!! tip

      AI tools are very good at CSS. Describe what you want, and they can help generate it.

## Tooltips on aggregated charts with `after_stat()`

Some geoms don't draw your rows directly: `geom_histogram`, for example, first **bins** the data, so there is one bar per bin instead of one element per row. Mapping a raw column to `tooltip` can't work there — you would have one label per source row but far fewer bars.

The solution is plotnine's [`after_stat()`](https://plotnine.org/reference/after_stat.html): it maps the tooltip to the values **computed by the stat**, which are aligned one-to-one with the drawn elements.

```py hl_lines="21 22 23 24 25"
from plotnine import (
    ggplot,
    aes,
    after_stat,
    geom_histogram,
    labs,
    theme_minimal,
    theme,
    element_text,
    element_blank,
)
from plotnine.data import diamonds

from ninejs import interactive, save

gg = (
    ggplot(
        diamonds,
        aes(
            x="carat",
            tooltip=after_stat(
                "'<b>' + count.astype(int).astype(str) + ' diamonds</b><br>'"
                " + xmin.round(2).astype(str) + ' to '"
                " + xmax.round(2).astype(str) + ' carats'"
            ),
        ),
    )
    + geom_histogram(binwidth=0.25, boundary=0, fill="#2a78d6", color="#ffffff")
    + labs(
        title="Most diamonds are under one carat",
        x="Carat",
        y="Number of diamonds",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(weight="bold", size=16),
        panel_grid_minor=element_blank(),
    )
)

interactive(gg) + save("docs/iframes/tooltip-after-stat.html")
```

<iframe width="100%" height="600" src="../iframes/tooltip-after-stat.html" style="border:none;"></iframe>

!!! tip

      This works with any stat, not just histograms: for example
      `geom_bar()` counts observations per category with `stat_count`, so
      `tooltip=after_stat("count.astype(int).astype(str) + ' rows'")`
      labels each bar with its count.

## HTML injection inside the tooltip

```py
df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5] * 2,
        "y": [2, 4, 3, 6, 5, 1, 3, 2, 5, 4],
        "category": ["Group A"] * 5 + ["Group B"] * 5,
    }
).with_columns(
    pl.format(
        """
        <i>The</i> <b>category</b> is <span style="color:red; font-size:24px;">{}</span>
        """,
        pl.col("category"),
    ).alias("tooltip")
)


gg = (
    ggplot(df, aes(x="x", y="y", color="category", tooltip="tooltip"))
    + geom_line(size=5)
    + theme_minimal()
    + labs(x="x", y="y", color="Category")
)

interactive(gg) + save("docs/iframes/tooltip-html-injection.html")
```

<iframe width="100%" height="600" src="../iframes/tooltip-html-injection.html" style="border:none;"></iframe>

Note that the HTML inside the tooltip is made "safe" via [DOMPurify](https://github.com/cure53/DOMPurify), which removes any `<script>` or `onclick` events for [security reasons](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS). If you want to add JavaScript, see the [dedicated guide](javascript.md).
