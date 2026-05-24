from plotnine import ggplot, aes, geom_point, theme_void, theme
from plotnine.data import anscombe_quartet

from ninejs import interactive, css, save

gg = (
    ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", color="dataset"))
    + geom_point(size=30, alpha=0.5)
    + theme_void()
    + theme(legend_position="none", figure_size=(8, 5))
)

goo_css = """
svg {filter: contrast(20);}

.point {
    filter: blur(5px);
    animation: goo 3s ease-in-out infinite alternate;
}
.point:nth-child(2n) {animation-duration: 4s;}
.point:nth-child(3n) {animation-duration: 8s;}

@keyframes goo {
    from {transform: translate(-12px, -12px) scale(1);}
    to {transform: translate(12px, 12px) scale(1.3);}
}
"""

interactive(gg) + css(goo_css) + save("docs/iframes/animation-art.html", minify=True)
