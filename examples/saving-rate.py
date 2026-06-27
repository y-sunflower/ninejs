from plotnine import aes, geom_line, geom_point, ggplot, labs, theme_minimal
from plotnine.data import economics

from ninejs import interactive, save


df = economics[economics["date"].dt.year >= 2000].copy()
df["tooltip"] = [
    f"{date:%b %Y}<br>Saving rate: {value:.1f}%"
    for date, value in zip(df["date"], df["psavert"], strict=True)
]

gg = (
    ggplot(df, aes("date", "psavert"))
    + geom_line(color="#2f6f73", size=1)
    + geom_point(aes(tooltip="tooltip"), color="#d95f02", size=3, alpha=0.7)
    + labs(title="U.S. personal saving rate since 2000", x="", y="Saving rate (%)")
    + theme_minimal()
)

interactive(gg, hover_nearest=True) + save("docs/iframes/saving-rate.html")
