from plotnine import (
    ggplot,
    aes,
    geom_point,
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
df["tooltip"] = df["category"].astype(str) + " (" + df["value"].astype(str) + ")"


gg = (
    ggplot(df, aes(x="category", y="value", tooltip="tooltip"))
    + geom_col()
    + theme_classic()
)

interactive(gg) + save("docs/iframes/bar.html")
