from plotnine import aes, geom_point, ggplot, theme_minimal
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
            data_id="dataset",
        ),
    )
    + geom_point(size=7, alpha=0.5)
    + theme_minimal()
)

(
    interactive(gg)
    + css(from_dict={".tooltip": {"font-size": "3em"}})
    + save("docs/iframes/quickstart2.html", minify=True)
)
