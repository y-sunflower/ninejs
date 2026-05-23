from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import interactive, save

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

interactive(gg) + save("docs/iframes/on-click-new-window.html", minify=True)
