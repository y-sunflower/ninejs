---
title: CO2 Emissions in Europe
---

- [Source of the original code](https://python-graph-gallery.com/web-map-with-custom-legend/)
- Author: [Joseph Barbier](https://www.ysunflower.com/)

The lines of code where `ninejs` is used are highlighted (only three, including the import); everything else is part of the original code.

```py hl_lines="7 95 131"
import geopandas as gp
import pandas as pd
import plotnine as gg
from pyfonts import load_google_font, set_default_font
from pypalettes import load_palette

from ninejs import interactive, save


set_default_font(load_google_font("Fira Sans"))
cmap_colors = load_palette("BrwnYl")


def good_centroid(geometry):
    projected = geometry.to_crs(epsg=3035)
    centroids = projected.geometry.centroid
    return gp.GeoSeries(centroids, crs=projected.crs).to_crs(geometry.crs)


world = gp.read_file(
    "https://raw.githubusercontent.com/holtzy/the-python-graph-gallery/master/static/data/europe.geojson"
)
co2 = pd.read_csv(
    "https://raw.githubusercontent.com/holtzy/the-python-graph-gallery/master/static/data/co2PerCapita.csv"
)

data = world.merge(co2, how="left", left_on="name", right_on="Country")
data = data[data["continent"] == "Europe"]
data = data[~data["name"].isin(["Russia", "Iceland"])]
data = data[data["Year"] == 2021]
data = data[["name", "Total", "geometry"]].dropna()
data["tooltip"] = data.apply(lambda row: f"{row['name']}: {row['Total']:.2f} t", axis=1)

centroids = good_centroid(data)
data["center_lon"] = centroids.x
data["center_lat"] = centroids.y

countries_to_annotate = [
    "France",
    "Italy",
    "Romania",
    "Poland",
    "Finland",
    "Ukraine",
    "Spain",
    "Germany",
    "Sweden",
    "United Kingdom",
    "Belarus",
    "Norway",
]

labels = data[data["name"].isin(countries_to_annotate)].copy()
adjustments = {
    "France": (10, 3),
    "Italy": (-2.4, 2.5),
    "Finland": (0, -2),
    "Belarus": (0, -0.4),
    "Ireland": (0, -1),
    "Germany": (-0.2, 0),
    "Poland": (0, 0.2),
    "Sweden": (-1.2, -2.8),
    "United Kingdom": (1, -1.5),
    "Norway": (-4, -5.5),
}

for country, (x_adjust, y_adjust) in adjustments.items():
    country_rows = labels["name"] == country
    labels.loc[country_rows, "center_lon"] += x_adjust
    labels.loc[country_rows, "center_lat"] += y_adjust

labels["country_label"] = labels["name"].replace({"United Kingdom": "UK"}).str.upper()
labels["label"] = [
    f"{country}: {total:.2f}"
    for country, total in zip(labels["country_label"], labels["Total"])
]
labels["label_color"] = labels["Total"].map(
    lambda value: "#ffffff" if value > 7 else "#000000"
)

plot = (
    gg.ggplot(data)
    + gg.geom_map(
        gg.aes(fill="Total", tooltip="tooltip", data_id="name"),
        color="black",
        size=0.25,
    )
    + gg.geom_text(
        data=labels,
        mapping=gg.aes(
            x="center_lon",
            y="center_lat",
            label="label",
            color="label_color",
            tooltip="tooltip",
        ),
        size=7,
        fontweight="bold",
        show_legend=False,
    )
    + gg.annotate(
        "text",
        x=15,
        y=32,
        label="CO2 emissions per capita in Europe (2021)",
        size=16,
        fontweight="bold",
        ha="center",
    )
    + gg.annotate(
        "text",
        x=15,
        y=30.5,
        label="Unit: metric tons | Data: zenodo.org | Viz: barbierjoseph.com",
        size=10,
        ha="center",
    )
    + gg.scale_fill_gradientn(colors=cmap_colors, limits=(0, 15))
    + gg.scale_color_identity()
    + gg.coord_cartesian(xlim=(-11, 41), ylim=(24, 73), expand=False)
    + gg.theme_void(base_size=8)
    + gg.theme(
        figure_size=(8.2, 10),
        legend_position="none",
        plot_background=gg.element_rect(fill="white", color="white"),
        panel_background=gg.element_rect(fill="white", color="white"),
        plot_margin=0.01,
    )
)

interactive(plot) + save("docs/iframes/europe-co2.html")
```

<iframe width="100%" height="800" src="../iframes/europe-co2.html" style="border:none;"></iframe>
