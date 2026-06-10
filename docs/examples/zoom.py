from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import mpg

from ninejs import interactive, save

p = (
    ggplot(
        mpg,
        aes(x="displ", y="hwy", color="drv", tooltip="model"),
    )
    + geom_point(size=3, alpha=0.7)
    + theme_minimal()
)

interactive(p, zoomable=True) + save("docs/iframes/zoom.html")
