from plotnine import (
    ggplot,
    aes,
    geom_point,
    geom_smooth,
    facet_wrap,
    labs,
    scale_y_continuous,
    coord_fixed,
    theme_tufte,
    theme,
    element_line,
    element_blank,
    theme_minimal,
    geom_line,
    geom_col,
    theme_classic,
)
from plotnine.data import anscombe_quartet
import pandas as pd

from ninejs import interactive, css, save

gg = (
    ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", tooltip="dataset"))
    + geom_point(size=7, alpha=0.5)
    + theme_minimal()
)

(interactive(gg) + css(".tooltip{font-size: 2em;}") + save("docs/iframes/point.html"))

#################


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
    interactive(gg)
    + css(from_dict={".tooltip": {"font-size": "3em"}})
    + save("docs/iframes/quickstart2.html")
)


################
gg = (
    ggplot(
        data=anscombe_quartet,
        mapping=aes(
            x="x",
            y="y",
            color="dataset",
            tooltip="dataset",
        ),
    )
    + geom_line(size=4, alpha=0.5)
    + theme_minimal()
)

(
    interactive(gg)
    + css(from_dict={".tooltip": {"font-size": "3em"}})
    + save("docs/iframes/line.html")
)

################

df = pd.DataFrame({"category": ["A", "B", "C"], "value": [3, 7, 5]})
df["tooltip"] = [
    f"{category} ({value})"
    for category, value in zip(df["category"], df["value"], strict=True)
]


gg = (
    ggplot(df, aes(x="category", y="value", tooltip="tooltip"))
    + geom_col()
    + theme_classic()
)

interactive(gg) + save("docs/iframes/bar.html")

################


plot = (
    ggplot(anscombe_quartet, aes("x", "y", tooltip="x"))
    + geom_smooth(method="lm", se=False, fullrange=True, color="steelblue", size=1)
    + geom_point(color="sienna", fill="orange", size=3)
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
