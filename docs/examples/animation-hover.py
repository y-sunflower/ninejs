from plotnine import aes, geom_point, ggplot, theme_minimal
from plotnine.data import mpg

from ninejs import css, interactive, save

gg = (
    ggplot(
        mpg,
        aes(
            x="cty",
            y="hwy",
            tooltip="manufacturer",
            hover_group="manufacturer",
        ),
    )
    + geom_point(size=6, alpha=0.6, color="#F58518")
    + theme_minimal()
)

hover_css = """
.plot-element {
    transition: opacity 0.3s ease, filter 0.3s ease, transform 0.3s ease;
}

.hovered {
    filter: drop-shadow(0 0 1px purple);
    transform: scale(1.2);
}
"""

(
    interactive(gg)
    + css(hover_css)
    + save("docs/iframes/animation-hover.html", minify=True)
)
