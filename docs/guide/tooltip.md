`ninejs` lets you easily customize the tooltip (e.g., the thing that appears when hovering an element) using HTML and CSS.

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

But we can make it look better thanks to **CSS**. If you're completely unfamiliar with CSS, check out [this other guide](css.md).

```py
(
    interactive(gg)
    + css(".tooltip {background-color: #FFC300; color: #421173;}")
    + save("docs/iframes/tooltip-custom-css.html", minify=True)
)
```

<iframe width="100%" height="600" src="../iframes/tooltip-custom-css.html" style="border:none;"></iframe>

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
    + save("docs/iframes/tooltip-custom-css2.html", minify=True)
)
```

<iframe width="100%" height="600" src="../iframes/tooltip-custom-css2.html" style="border:none;"></iframe>

!!! tip

      AI is crazy good at CSS! Just describe what you want and it'll be able to do it for sure.
