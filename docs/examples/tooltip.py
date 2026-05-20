from plotnine import aes, geom_point, ggplot, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import css, interactive, save

gg = (
    ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", tooltip="dataset"))
    + geom_point(size=7, alpha=0.5)
    + theme_minimal()
)

(interactive(gg) + css(".tooltip{font-size: 2em;}") + save("docs/iframes/point.html"))
