from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet as df

from ninejs import interactive, save

df["alert"] = "alert('You clicked on: " + df["dataset"] + "');"

gg = (
    ggplot(
        data=df,
        mapping=aes(x="x", y="y", color="dataset", tooltip="dataset", on_click="alert"),
    )
    + geom_point(size=7, alpha=0.7)
    + theme_minimal()
)

interactive(gg) + save("docs/iframes/on-click-custom-alert.html", minify=True)
