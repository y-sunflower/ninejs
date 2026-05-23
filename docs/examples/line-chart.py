from plotnine import aes, geom_line, ggplot, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import css, interactive, save

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
    + save("docs/iframes/line.html", minify=True)
)
