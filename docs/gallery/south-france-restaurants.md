---
title: South of France Restaurants
---

- [Source of the original code](https://r-graph-gallery.com/327-chloropleth-map-from-geojson-with-ggplot2.html)
- Author: [Yan Holtz](https://www.yan-holtz.com/)

```py
import geopandas as gp
import pandas as pd
import plotnine as gg

from ninejs import interactive, save, css


geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/communes.geojson"
data_url = "https://raw.githubusercontent.com/holtzy/R-graph-gallery/master/DATA/data_on_french_states.csv"
departments = ["06", "83", "13", "30", "34", "11", "66"]
background_color = "#f5f5f2"
text_color = "#34322f"

communes = gp.read_file(geo_url)
communes = communes[communes["code"].str[:2].isin(departments)].copy()

restaurants = pd.read_csv(data_url, sep=";")
restaurants = restaurants.groupby("depcom", as_index=False)["nb_equip"].sum()

data = communes.merge(restaurants, how="left", left_on="code", right_on="depcom")
data["nb_equip"] = data["nb_equip"].fillna(0).astype(int)
data["fill_value"] = data["nb_equip"].clip(lower=0.1)
data["tooltip"] = [
    f"{name}: {value:,} restaurants" if value else f"{name}: no restaurants"
    for name, value in zip(data["nom"], data["nb_equip"])
]

data = data.to_crs(epsg=2154)
labels = data[
    data["nom"].isin(
        [
            "Nice",
            "Montpellier",
            "Cannes",
            "Aix-en-Provence",
            "Nîmes",
            "Toulon",
            "Perpignan",
        ]
    )
].copy()
points = labels.geometry.representative_point()
labels = labels.set_geometry(points).to_crs(epsg=4326)
labels["lon"] = labels.geometry.x
labels["lat"] = labels.geometry.y
label_positions = pd.DataFrame(
    {
        "nom": [
            "Nice",
            "Montpellier",
            "Cannes",
            "Aix-en-Provence",
            "Nîmes",
            "Toulon",
            "Perpignan",
        ],
        "label_x": [7.18, 3.35, 6.72, 5.10, 4.30, 6.15, 2.20],
        "label_y": [44.18, 44.00, 43.48, 43.70, 44.42, 42.98, 42.58],
    }
)
labels = labels.merge(label_positions, on="nom")
labels["label"] = labels.apply(
    lambda row: f"{row['nom']}\n{row['nb_equip']:,}",
    axis=1,
)

data["geometry"] = data.geometry.simplify(650, preserve_topology=True)
data = data.to_crs(epsg=4326)
caption = "Data: INSEE | Design: Yan Holtz | r-graph-gallery.com"

plot = (
    gg.ggplot(data)
    + gg.geom_map(
        gg.aes(fill="fill_value", tooltip="tooltip", hover_group="code"),
        color="white",
        size=0.03,
        alpha=0.95,
    )
    + gg.geom_segment(
        data=labels,
        mapping=gg.aes(x="label_x", y="label_y", xend="lon", yend="lat"),
        inherit_aes=False,
        color=text_color,
        size=0.35,
    )
    + gg.geom_label(
        data=labels,
        mapping=gg.aes(x="label_x", y="label_y", label="label"),
        inherit_aes=False,
        fill=background_color,
        color=text_color,
        size=7.5,
        label_size=0,
        fontweight="bold",
    )
    + gg.annotate(
        "text",
        x=1.32,
        y=44.80,
        label="South of France\nrestaurant concentration",
        ha="left",
        va="top",
        size=18,
        fontweight="bold",
        color=text_color,
    )
    + gg.annotate(
        "text",
        x=1.32,
        y=44.32,
        label=(
            "Municipality totals, shown on a log color scale\n"
            "to keep small towns visible beside coastal hubs."
        ),
        ha="left",
        va="top",
        size=8.5,
        color=text_color,
    )
    + gg.annotate(
        "text",
        x=1.32,
        y=42.25,
        label=caption,
        ha="left",
        va="bottom",
        size=6.5,
        color=text_color,
    )
    + gg.scale_fill_cmap(
        "viridis",
        name="Restaurants",
        trans="log10",
        limits=(0.1, 2300),
        breaks=[0.1, 1, 10, 100, 1000],
        labels=["0", "1", "10", "100", "1,000"],
    )
    + gg.guides(fill=gg.guide_colorbar(direction="horizontal"))
    + gg.coord_cartesian(xlim=(1.2, 7.85), ylim=(42.15, 44.90), expand=False)
    + gg.theme_void(base_size=8)
    + gg.theme(
        figure_size=(10, 6),
        legend_position="none",
        plot_background=gg.element_rect(fill=background_color, color=background_color),
        panel_background=gg.element_rect(fill=background_color, color=background_color),
        plot_margin=0.02,
    )
)

(
    interactive(plot, hover_nearest=True)
    + css(from_dict={".tooltip": {"font-size": "1.2em"}})
    + save("docs/iframes/south-france-restaurants.html")
)
```

<iframe width="100%" height="600" src="../iframes/south-france-restaurants.html" style="border:none;"></iframe>
