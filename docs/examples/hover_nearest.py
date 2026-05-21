from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import interactive, save

gg = (
    ggplot(
        data=anscombe_quartet,
        mapping=aes(
            x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset"
        ),
    )
    + geom_point(size=7, alpha=0.5)
    + theme_minimal()
)

interactive(gg, hover_nearest=True) + save(
    "docs/iframes/hover-neareast.html", minify=True
)
