import pandas as pd
from plotnine import (
    aes,
    geom_area,
    geom_text,
    ggplot,
    position_stack,
    scale_fill_manual,
    theme_minimal,
)

from ninejs import css, interactive, javascript, save
from ninejs.data import revenue

aggregate = revenue.groupby(["month", "group"], as_index=False)["value"].sum()
label_data = revenue[revenue["month"] == pd.Timestamp("2025-07-01 00:00:00")]

colors = {
    "Online subscriptions": "#56B4E9",
    "Online services": "#0072B2",
    "Retail stores": "#E69F00",
    "Retail partners": "#D55E00",
    "Online revenue": "#009E73",
    "Retail revenue": "#CC79A7",
}

gg = (
    ggplot(revenue, aes(tooltip="category", data_id="group"))
    + geom_area(aes(x="month", y="value", fill="category", group="category"), alpha=0.9)
    + geom_text(
        label_data,
        aes(x="month", y="value", label="category", group="category"),
        inherit_aes=False,
        position=position_stack(vjust=0.3),
        color="white",
        size=9,
    )
    + geom_area(
        aggregate,
        aes(
            x="month",
            y="value",
            fill="group",
            group="group",
            tooltip="group",
            data_id="group",
        ),
        alpha=1,
    )
    + scale_fill_manual(values=colors, breaks=["Online revenue", "Retail revenue"])
    + theme_minimal()
)


(
    interactive(gg, reverse_hover=True)
    + css(from_file="docs/examples/area_hover_to_show.css")
    + javascript(from_file="docs/examples/area_hover_to_show.js")
    + save("docs/iframes/area-hover-to-show.html", minify=True)
)
