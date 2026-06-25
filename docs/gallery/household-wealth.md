---
title: Household Wealth
---

- [Source of the original code](https://r-graph-gallery.com/web-stacked-area-chart-inline-labels.html)
- Author: [Gilbert Fontana](https://twitter.com/GilbertFontana)

The lines of code where `ninejs` is used are highlighted.

```py hl_lines="4 84 176"
import pandas as pd
import plotnine as gg

from ninejs import interactive, save


data = pd.read_csv("docs/examples/household-wealth.csv")
order = ["United States", "China", "Japan", "Germany", "United Kingdom", "France", "India", "Other"]

palette = {
    "United States": "#003f5c",
    "China": "#2f4b7c",
    "Japan": "#665191",
    "Germany": "#a05195",
    "United Kingdom": "#d45087",
    "France": "#f95d6a",
    "India": "#ff7c43",
    "Other": "#ffa600",
}
display_names = {"United States": "USA", "United Kingdom": "UK", "Other": "Rest of the world"}

data["country"] = pd.Categorical(data["country"], categories=order, ordered=True)
data = data.sort_values(["year", "country"])
data["tooltip"] = [
    f"{display_names.get(str(country), str(country))}: ${value:,.0f}B"
    for country, value in zip(data["country"], data["total_wealth"])
]

totals = data.groupby("year", as_index=False)["total_wealth"].sum()
markers = totals[totals["year"].isin([2000, 2005, 2010, 2015, 2021])].copy()
line_offsets = {
    2000: 20000,
    2005: 20000,
    2010: 20000,
    2015: 25000,
    2021: 50000,
}
label_offsets = {
    2000: 30000,
    2005: 30000,
    2010: 30000,
    2015: 35000,
    2021: 50000,
}
markers["line_y"] = markers["total_wealth"] + markers["year"].map(line_offsets)
markers["label_y"] = markers["total_wealth"] + markers["year"].map(label_offsets)
markers["label"] = markers["total_wealth"].map(lambda value: f"${value:,.0f}B")
markers["label_x"] = markers["year"].astype(float)
markers.loc[markers["year"] == 2000, "label_x"] = 2000.45

latest_values = (
    data[data["year"] == 2021]
    .assign(country_name=lambda frame: frame["country"].astype(str))
    .set_index("country_name")["total_wealth"]
    .to_dict()
)
inline_labels = pd.DataFrame(
    {
        "country": order,
        "x": [2021.35] * 8,
        "y": [420000, 300000, 245000, 220000, 200000, 183000, 165000, 80000],
    }
)
inline_labels["label"] = [
    f"{display_names.get(country, country)} ${latest_values[country]:,.0f}B"
    for country in inline_labels["country"]
]
inline_labels["color"] = inline_labels["country"].map(palette)

x_axis = pd.DataFrame(
    {
        "year": [2000, 2005, 2010, 2015, 2021],
        "label": ["2000", "2005", "2010", "2015", "2021"],
    }
)
caption = (
    "Data: James Davies, Rodrigo Lluberas and Anthony Shorrocks, "
    "Credit Suisse Global Wealth Databook 2022\nDesign: Gilbert Fontana"
)

plot = (
    gg.ggplot(data, gg.aes(x="year", y="total_wealth"))
    + gg.geom_area(
        gg.aes(fill="country", group="country", tooltip="tooltip", hover_group="country"),
        color="white",
        size=0.18,
    )
    + gg.geom_segment(
        data=markers,
        mapping=gg.aes(x="year", xend="year", y=0, yend="line_y"),
        inherit_aes=False,
        color="black",
        size=0.7,
    )
    + gg.geom_point(
        data=markers,
        mapping=gg.aes(x="year", y="line_y"),
        inherit_aes=False,
        color="black",
        size=2.2,
    )
    + gg.geom_text(
        data=markers[markers["year"] < 2021],
        mapping=gg.aes(x="label_x", y="label_y", label="label"),
        inherit_aes=False,
        color="black",
        size=8,
        fontweight="bold",
        va="bottom",
    )
    + gg.geom_text(
        data=markers[markers["year"] == 2021],
        mapping=gg.aes(x="year", y="label_y", label="label"),
        inherit_aes=False,
        color="black",
        size=8,
        fontweight="bold",
        ha="right",
        va="center",
    )
    + gg.geom_text(
        data=inline_labels,
        mapping=gg.aes(x="x", y="y", label="label", color="color"),
        inherit_aes=False,
        size=8,
        fontweight="bold",
        ha="left",
        va="center",
        show_legend=False,
    )
    + gg.geom_text(
        data=x_axis,
        mapping=gg.aes(x="year", y=-16000, label="label"),
        inherit_aes=False,
        color="black",
        size=8,
        va="top",
    )
    + gg.annotate("segment", x=2000, xend=2021, y=0, yend=0, color="black", size=0.7)
    + gg.annotate(
        "text",
        x=2000,
        y=505000,
        label="Aggregated\nHousehold\nWealth",
        ha="left",
        va="top",
        size=21,
        fontweight="bold",
        color="black",
    )
    + gg.annotate(
        "text",
        x=2000,
        y=-60000,
        label=caption,
        ha="left",
        va="top",
        size=7.5,
        color="black",
    )
    + gg.scale_fill_manual(values=palette)
    + gg.scale_color_identity()
    + gg.scale_x_continuous(limits=(1999.5, 2026.5))
    + gg.scale_y_continuous(limits=(-90000, 540000), expand=(0, 0))
    + gg.coord_cartesian(expand=False)
    + gg.theme_void(base_size=8)
    + gg.theme(
        legend_position="none",
        figure_size=(10, 6),
        plot_background=gg.element_rect(fill="white", color="white"),
        panel_background=gg.element_rect(fill="white", color="white"),
        plot_margin=0.03,
    )
)

interactive(plot) + save("docs/iframes/household-wealth.html", minify=True)
```

<iframe width="100%" height="600" src="../iframes/household-wealth.html" style="border:none;"></iframe>
