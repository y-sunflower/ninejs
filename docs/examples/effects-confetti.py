from plotnine import aes, geom_point, ggplot, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import effects, interactive, save

anscombe_quartet["confetti"] = effects.confetti()

gg = (
    ggplot(
        data=anscombe_quartet,
        mapping=aes(
            x="x", y="y", color="dataset", tooltip="dataset", on_click="confetti"
        ),
    )
    + geom_point(size=7, alpha=0.7)
    + theme_minimal()
)

interactive(gg) + save("docs/iframes/effects-confetti.html")
