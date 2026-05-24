from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet as df

from ninejs import interactive, save, css

df["stroke"] = "event.target.classList.toggle('selected')"

gg = (
    ggplot(
        data=df,
        mapping=aes(
            x="x",
            y="y",
            color="dataset",
            tooltip="dataset",
            on_click="stroke",
        ),
    )
    + geom_point(size=7, alpha=0.7)
    + theme_minimal()
)

(
    interactive(gg)
    + css(from_dict={".selected": {"stroke": "black", "stroke-width": "1px"}})
    + save("docs/iframes/on-click-stroke.html", minify=True)
)
