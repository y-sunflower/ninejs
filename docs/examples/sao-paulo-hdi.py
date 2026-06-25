import geopandas as gp
import numpy as np
import pandas as pd
import plotnine as gg

from ninejs import css, interactive, save


breaks = np.arange(0.65, 0.951, 0.05)
group_labels = {
    "0": "0.650 or less",
    "1": "0.650 to 0.699",
    "2": "0.700 to 0.749",
    "3": "0.750 to 0.799",
    "4": "0.800 to 0.849",
    "5": "0.850 to 0.899",
    "6": "0.900 to 0.949",
    "7": "0.950 or more",
}
palette = {
    "0": "#ffffcc",
    "1": "#d9f0a3",
    "2": "#addd8e",
    "3": "#78c679",
    "4": "#41ab5d",
    "5": "#238443",
    "6": "#006837",
    "7": "#004529",
}

atlas_data = pd.read_csv("docs/examples/atlas_sp_hdi.csv")
atlas = gp.GeoDataFrame(
    atlas_data.drop(columns="geometry"),
    geometry=gp.GeoSeries.from_wkt(atlas_data["geometry"]),
    crs="EPSG:4326",
)
atlas["group_hdi"] = np.searchsorted(breaks, atlas["HDI"], side="right").astype(str)
atlas["group_label"] = atlas["group_hdi"].map(group_labels)
atlas["tooltip"] = [
    f"HDI: {hdi:.3f}<br>Range: {label}"
    for hdi, label in zip(atlas["HDI"], atlas["group_label"])
]

pop_hdi = (
    atlas.drop(columns="geometry")
    .groupby(["group_hdi", "group_label"], as_index=False, observed=True)["pop"]
    .sum()
    .sort_values("group_hdi")
)
pop_hdi["share"] = pop_hdi["pop"] / pop_hdi["pop"].sum() * 100
pop_hdi["label"] = pop_hdi["share"].map(lambda value: f"{value:.1f}%")
pop_hdi["tooltip"] = [
    f"{label}<br>Population share: {share:.1f}%"
    for label, share in zip(pop_hdi["group_label"], pop_hdi["share"])
]

x_min, y_min, x_max, y_max = atlas.total_bounds
x_span = x_max - x_min
y_span = y_max - y_min

inset_left = x_min + x_span * 0.52
inset_right = x_min + x_span * 0.97
inset_bottom = y_min + y_span * 0.10
inset_top = y_min + y_span * 0.48
bar_slot = (inset_right - inset_left) / len(pop_hdi)
bar_width = bar_slot * 0.72
max_share = pop_hdi["share"].max()

pop_hdi["bar_x"] = inset_left + bar_slot * (np.arange(len(pop_hdi)) + 0.5)
pop_hdi["xmin"] = pop_hdi["bar_x"] - bar_width / 2
pop_hdi["xmax"] = pop_hdi["bar_x"] + bar_width / 2
pop_hdi["ymin"] = inset_bottom
pop_hdi["ymax"] = inset_bottom + (pop_hdi["share"] / max_share) * (
    inset_top - inset_bottom
)
pop_hdi["label_y"] = pop_hdi["ymax"] + y_span * 0.025
pop_hdi["axis_y"] = inset_bottom - y_span * 0.045
pop_hdi["title_y"] = inset_top + y_span * 0.065

caption = "Source: Atlas Brasil | Original design: R Graph Gallery"

plot = (
    gg.ggplot()
    + gg.geom_map(
        data=atlas,
        mapping=gg.aes(fill="group_hdi", tooltip="tooltip", hover_key="group_hdi"),
        color="white",
        size=0.05,
    )
    + gg.geom_rect(
        data=pop_hdi,
        mapping=gg.aes(
            xmin="xmin",
            xmax="xmax",
            ymin="ymin",
            ymax="ymax",
            fill="group_hdi",
            tooltip="tooltip",
            hover_key="group_hdi",
        ),
        color=None,
    )
    + gg.geom_text(
        data=pop_hdi,
        mapping=gg.aes(x="bar_x", y="label_y", label="label"),
        size=5.5,
        color="#1f2933",
    )
    + gg.geom_text(
        data=pop_hdi,
        mapping=gg.aes(x="bar_x", y="axis_y", label="group_label"),
        size=4.2,
        angle=45,
        ha="right",
        color="#374151",
    )
    + gg.annotate(
        "text",
        x=(inset_left + inset_right) / 2,
        y=pop_hdi["title_y"].iloc[0],
        label="Population share",
        size=9,
        fontweight="bold",
        ha="center",
    )
    + gg.annotate(
        "text",
        x=x_min + x_span * 0.50,
        y=y_max + y_span * 0.10,
        label="HDI in Sao Paulo, BR (2010)",
        size=16,
        fontweight="bold",
        ha="center",
    )
    + gg.annotate(
        "text",
        x=x_min + x_span * 0.50,
        y=y_max + y_span * 0.04,
        label="Microregion HDI in Sao Paulo",
        size=8.5,
        color="#4b5563",
        ha="center",
    )
    + gg.annotate(
        "text",
        x=inset_right,
        y=y_min + y_span * 0.01,
        label=caption,
        size=5.5,
        color="#6b7280",
        ha="right",
    )
    + gg.scale_fill_manual(values=palette, guide=None)
    + gg.coord_cartesian(
        xlim=(x_min, x_max),
        ylim=(y_min - y_span * 0.08, y_max + y_span * 0.15),
        expand=False,
    )
    + gg.theme_void(base_size=9)
    + gg.theme(
        figure_size=(5.5, 8),
        plot_background=gg.element_rect(fill="#f7f7f2", color="#f7f7f2"),
        panel_background=gg.element_rect(fill="#f7f7f2", color="#f7f7f2"),
        plot_margin=0.02,
    )
)

(
    interactive(plot)
    + css(
        from_dict={
            ".plot-element": {
                "transition": "opacity 120ms ease, stroke-width 120ms ease"
            },
            ".plot-element.hovered": {"stroke": "orange", "stroke-width": "1.2px"},
            ".plot-element.not-hovered": {"opacity": "0.5"},
            ".tooltip": {"font-size": "13px"},
        }
    )
    + save("docs/iframes/sao-paulo-hdi.html", minify=True)
)
