from plotnine import aes, geom_point, ggplot, labs, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import interactive, show

gg = (
    ggplot(
        anscombe_quartet,
        aes(x="x", y="y", color="dataset", tooltip="dataset"),
    )
    + geom_point(size=5, alpha=0.7)
    + labs(x="x", y="y")
    + theme_minimal()
)

fig = gg.draw()
ax = fig.axes[0]

ax.annotate(
    "Added with Matplotlib",
    xy=(16, 8),
    xytext=(12, 11),
    arrowprops={"arrowstyle": "->", "color": "#222222"},
    color="#222222",
)

interactive(gg, bbox_inches="tight") + show()
# interactive(gg) + save("docs/iframes/matplotlib-annotation.html", minify=True)
