from plotnine import (
    ggplot,
    aes,
    geom_point,
    geom_line,
    labs,
    facet_wrap,
    theme_minimal,
    theme,
    element_text,
    scale_fill_manual,
)
from ninejs import interactive, save, css
import polars as pl

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

interactive(gg) + save("docs/iframes/tooltip-default.html", minify=True)

(
    interactive(gg)
    + css(".tooltip {background-color: #FFC300; color: #421173;}")
    + save("docs/iframes/tooltip-custom-css.html", minify=True)
)

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

interactive(gg) + save("docs/iframes/tooltip-html-injection.html", minify=True)
