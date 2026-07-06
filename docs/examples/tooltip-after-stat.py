from plotnine import (
    ggplot,
    aes,
    after_stat,
    geom_histogram,
    labs,
    theme_minimal,
    theme,
    element_text,
    element_blank,
)
from plotnine.data import diamonds

from ninejs import interactive, save

gg = (
    ggplot(
        diamonds,
        aes(
            x="carat",
            tooltip=after_stat(
                "'<b>' + count.astype(int).astype(str) + ' diamonds</b><br>'"
                " + xmin.round(2).astype(str) + ' to '"
                " + xmax.round(2).astype(str) + ' carats'"
            ),
        ),
    )
    + geom_histogram(binwidth=0.25, boundary=0, fill="#2a78d6", color="#ffffff")
    + labs(
        title="Most diamonds are under one carat",
        x="Carat",
        y="Number of diamonds",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(weight="bold", size=16),
        panel_grid_minor=element_blank(),
    )
)

interactive(gg) + save("docs/iframes/tooltip-after-stat.html", minify=True)
