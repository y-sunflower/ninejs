---
title: Unemployment rate in Belgium
---

- Author of the original chart: [Koen Van den Eeckhout](https://www.koenvandeneeckhout.be/)
- Made interactive with [ninejs](../index.md)

The lines of code where `ninejs` is used are highlighted (only four, including the import); everything else is part of the original code.

```py
import unicodedata

import geopandas as gpd
import numpy as np
import pandas as pd
import plotnine as gg

from ninejs import interactive, save, css


BELGIUM_URL = (
    "https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/"
    "refs/heads/master/static/data/belgium.json"
)
RATES_URL = (
    "https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/"
    "refs/heads/master/static/data/belgium-unemployment.csv"
)

PALETTE = [
    "#FCFCBD",
    "#FED69A",
    "#FDC48C",
    "#FB9A70",
    "#C74370",
    "#9D2D7A",
    "#86277A",
    "#661d5c",
    "#5A1A74",
]


def remove_accents(text: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )


belgium = gpd.read_file(BELGIUM_URL, layer="municipalities").drop(
    columns=[
        "prov_nis",
        "prov_fr",
        "prov_nl",
        "arr_nis",
        "id",
        "reg_nis",
        "reg_nl",
        "reg_fr",
        "arr_fr",
        "arr_nl",
        "nis",
    ],
    errors="ignore",
)
belgium = belgium.set_crs("EPSG:4326")
belgium["name_key"] = belgium["name_nl"].apply(remove_accents).str.lower()


def key(s):
    return (
        s.str.normalize("NFKD")
        .str.encode("ascii", "ignore")
        .str.decode("ascii")
        .str.lower()
    )


drop_cols = [
    "prov_nis",
    "prov_fr",
    "prov_nl",
    "arr_nis",
    "id",
    "reg_nis",
    "reg_nl",
    "reg_fr",
    "arr_fr",
    "arr_nl",
    "nis",
]

belgium = (
    gpd.read_file(BELGIUM_URL, layer="municipalities")
    .drop(columns=drop_cols, errors="ignore")
    .set_crs("EPSG:4326")
    .assign(name_key=lambda d: key(d["name_nl"]))
)

rates = pd.read_csv(RATES_URL).assign(name_key=lambda d: key(d["Gemeente"]))

df = (
    belgium.merge(rates, on="name_key", how="left")
    .rename(columns={"Werkloosheidsgraad": "unemployment_rate"})
    .to_crs("EPSG:3857")
    .assign(
        unemployment=lambda d: (
            pd.cut(
                d["unemployment_rate"],
                bins=np.arange(19),
                labels=[f"{i}-{i + 1}%" for i in range(18)],
                include_lowest=True,
                right=False,
            )
            .astype(object)
            .where(lambda s: s.notna(), None)
        ),
        tooltip=lambda d: np.where(
            d["unemployment_rate"].notna(),
            "<strong class='muni'>"
            + d["name_fr"]
            + "</strong><br>Unemployment: "
            + d["unemployment_rate"].round(2).astype(str)
            + "%",
            "<strong class='muni'>" + d["name_fr"] + "</strong><br>No data available",
        ),
    )
)


x_min, y_min, x_max, y_max = df.total_bounds
x_span, y_span = x_max - x_min, y_max - y_min

inset_left, inset_right = x_min + x_span * np.array([0.05, 0.45])
inset_bottom, inset_top = y_min + y_span * np.array([0.12, 0.38])
inset_width, inset_height = inset_right - inset_left, inset_top - inset_bottom

edges = np.arange(19)
counts, _ = np.histogram(df["unemployment_rate"].dropna(), bins=edges)

histogram = pd.DataFrame(
    {
        "count": counts,
        "edge_low": edges[:-1],
        "edge_high": edges[1:],
    }
).assign(
    rate_mid=lambda d: (d.edge_low + d.edge_high) / 2,
    unemployment=lambda d: d.edge_low.astype(str) + "-" + d.edge_high.astype(str) + "%",
    bar_center=lambda d: inset_left + d.rate_mid / 18 * inset_width,
    xmin=lambda d: d.bar_center - inset_width / 18 * 0.42,
    xmax=lambda d: d.bar_center + inset_width / 18 * 0.42,
    ymin=inset_bottom,
    ymax=lambda d: inset_bottom + d["count"] / d["count"].max() * inset_height,
    tooltip=lambda d: (
        d["count"].astype(str)
        + " municipalities have an unemployment rate of "
        + d.edge_low.astype(str)
        + "–"
        + d.edge_high.astype(str)
        + "%"
    ),
)

ticks = pd.DataFrame({"rate": np.arange(0, 19, 3)}).assign(
    label=lambda d: d.rate.astype(str).where(d.rate < 18, "18%"),
    x=lambda d: inset_left + d.rate / 18 * inset_width,
    y=inset_bottom,
    yend=inset_bottom - y_span * 0.01,
    label_y=inset_bottom - y_span * 0.035,
)

plot = (
    gg.ggplot()
    + gg.geom_rect(
        data=histogram,
        mapping=gg.aes(
            xmin="xmin",
            xmax="xmax",
            ymin="ymin",
            ymax="ymax",
            fill="rate_mid",
            tooltip="tooltip",
            hover_key="unemployment",
        ),
        color=None,
    )
    + gg.geom_segment(
        data=pd.DataFrame(
            {
                "x": [inset_left],
                "xend": [inset_right],
                "y": [inset_bottom],
                "yend": [inset_bottom],
            }
        ),
        mapping=gg.aes(x="x", xend="xend", y="y", yend="yend"),
        color="#222222",
        size=0.25,
    )
    + gg.geom_segment(
        data=ticks,
        mapping=gg.aes(x="x", xend="x", y="y", yend="yend"),
        color="#222222",
        size=0.25,
    )
    + gg.geom_text(
        data=ticks,
        mapping=gg.aes(x="x", y="label_y", label="label"),
        size=6,
        color="#222222",
    )
    + gg.geom_map(
        data=df,
        mapping=gg.aes(
            fill="unemployment_rate", tooltip="tooltip", hover_key="unemployment"
        ),
        color="#e6e6e6",
        size=0.08,
    )
    + gg.annotate(
        "text",
        x=x_min + x_span * 0.05,
        y=y_max + y_span * 0.10,
        label="Unemployment rate in Belgium",
        size=13,
        fontweight="bold",
        ha="left",
    )
    + gg.annotate(
        "text",
        x=x_min + x_span * 0.05,
        y=y_max + y_span * 0.055,
        label="By municipality, in December 2024",
        size=9,
        ha="left",
    )
    + gg.annotate(
        "text",
        x=x_min + x_span * 0.05,
        y=y_min + y_span * 0.03,
        label="Map: Koen Van den Eeckhout | Source: RVA (Interactive Statistics)",
        size=6,
        color="#909090",
        ha="left",
    )
    + gg.scale_fill_gradientn(
        colors=PALETTE,
        limits=(0, 18),
        na_value="#eeeeee",
        guide=None,
    )
    + gg.coord_equal(
        xlim=(x_min, x_max),
        ylim=(y_min - y_span * 0.02, y_max + y_span * 0.14),
        expand=False,
    )
    + gg.theme_void(base_size=9)
    + gg.theme(
        figure_size=(5.5, 7.5),
        plot_background=gg.element_rect(fill="white", color="white"),
        panel_background=gg.element_rect(fill="white", color="white"),
        plot_margin=0.02,
    )
)

(
    interactive(plot, hover_nearest=True)
    + css(
        from_dict={
            ".hovered": {"stroke": "#111", "stroke-width": "1px"},
            ".tooltip": {"font-size": "1.1em", "padding": "8px 10px"},
            ".muni": {"font-size": "1.15em"},
        }
    )
    + save("docs/iframes/map-belgium-unemployment.html")
)
```

<iframe width="95%" height="800" src="../iframes/map-belgium-unemployment.html" style="border:none;"></iframe>
