from plotnine import (
    aes,
    coord_fixed,
    element_blank,
    element_line,
    facet_wrap,
    geom_point,
    geom_smooth,
    ggplot,
    labs,
    scale_y_continuous,
    theme,
    theme_tufte,
)
from plotnine.data import anscombe_quartet

from ninejs import interactive, save

gg = (
    ggplot(anscombe_quartet, aes("x", "y", tooltip="x"))
    + geom_smooth(method="lm", se=False, fullrange=True, color="steelblue", size=1)
    + geom_point(color="sienna", fill="orange", size=3)
    + facet_wrap("dataset")
    + labs(title="Anscombe’s Quartet")
    + scale_y_continuous(breaks=(4, 8, 12))
    + coord_fixed(xlim=(3, 22), ylim=(2, 14))
    + theme_tufte(base_family="Futura", base_size=16)
    + theme(
        axis_line=element_line(color="#4d4d4d"),
        axis_ticks_major=element_line(color="#00000000"),
        axis_title=element_blank(),
        panel_spacing=0.09,
    )
)

interactive(gg) + save("docs/iframes/facet_wrap.html", minify=True)
