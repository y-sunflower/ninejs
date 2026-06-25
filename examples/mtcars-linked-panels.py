import numpy as np
import pandas as pd
import plotnine as gg
from plotnine.data import mtcars

from ninejs import css, interactive, save


def rescale(values: pd.Series) -> pd.Series:
    return (values - values.min()) / (values.max() - values.min())


scatter_view = "Displacement vs Quarter Mile"
bar_view = "Miles per Gallon by Car"

mtcars_db = mtcars.rename(columns={"name": "carname"}).copy()
mtcars_db["car_id"] = mtcars_db["carname"].str.replace(r"\W+", "-", regex=True)

scatter = mtcars_db.copy()
scatter["view"] = scatter_view
scatter["x"] = rescale(scatter["disp"])
scatter["y"] = rescale(scatter["qsec"])
scatter["tooltip"] = scatter["carname"]

bar = mtcars_db.sort_values("mpg").reset_index(drop=True).copy()
bar["view"] = bar_view
bar["y"] = (np.arange(len(bar)) + 0.5) / len(bar)
bar["ymin"] = bar["y"] - 0.36 / len(bar)
bar["ymax"] = bar["y"] + 0.36 / len(bar)
bar["xmin"] = 0
bar["xmax"] = bar["mpg"] / bar["mpg"].max()
bar["tooltip"] = [
    f"Car: {carname}<br>MPG: {mpg}"
    for carname, mpg in zip(bar["carname"], bar["mpg"], strict=True)
]

scatter_x_ticks = pd.DataFrame({"label": [100, 200, 300, 400]})
scatter_x_ticks["view"] = scatter_view
scatter_x_ticks["x"] = (scatter_x_ticks["label"] - scatter["disp"].min()) / (
    scatter["disp"].max() - scatter["disp"].min()
)
scatter_x_ticks["y"] = 0

scatter_y_ticks = pd.DataFrame({"label": [16, 18, 20, 22]})
scatter_y_ticks["view"] = scatter_view
scatter_y_ticks["x"] = 0
scatter_y_ticks["y"] = (scatter_y_ticks["label"] - scatter["qsec"].min()) / (
    scatter["qsec"].max() - scatter["qsec"].min()
)

bar_x_ticks = pd.DataFrame({"label": [10, 15, 20, 25, 30]})
bar_x_ticks["view"] = bar_view
bar_x_ticks["x"] = bar_x_ticks["label"] / bar["mpg"].max()
bar_x_ticks["y"] = 0

axis_segments = pd.DataFrame(
    [
        {"view": scatter_view, "x": 0, "xend": 1, "y": 0, "yend": 0},
        {"view": scatter_view, "x": 0, "xend": 0, "y": 0, "yend": 1},
        {"view": bar_view, "x": 0, "xend": 1, "y": 0, "yend": 0},
        {"view": bar_view, "x": 0, "xend": 0, "y": 0, "yend": 1},
    ]
)

scatter_x_tick_segments = scatter_x_ticks.assign(
    xend=scatter_x_ticks["x"],
    y=-0.01,
    yend=0.01,
)
scatter_y_tick_segments = scatter_y_ticks.assign(
    x=-0.01,
    xend=0.01,
    yend=scatter_y_ticks["y"],
)
bar_x_tick_segments = bar_x_ticks.assign(
    xend=bar_x_ticks["x"],
    y=-0.01,
    yend=0.01,
)
tick_segments = pd.concat(
    [scatter_x_tick_segments, scatter_y_tick_segments, bar_x_tick_segments],
    ignore_index=True,
)

axis_labels = pd.DataFrame(
    [
        {
            "view": scatter_view,
            "x": 0.5,
            "y": -0.075,
            "label": "Displacement",
            "angle": 0,
        },
        {
            "view": scatter_view,
            "x": -0.18,
            "y": 0.5,
            "label": "Quarter Mile",
            "angle": 90,
        },
        {
            "view": bar_view,
            "x": 0.5,
            "y": -0.075,
            "label": "Miles per Gallon",
            "angle": 0,
        },
    ]
)

plot = (
    gg.ggplot()
    + gg.geom_rect(
        data=bar,
        mapping=gg.aes(
            xmin="xmin",
            xmax="xmax",
            ymin="ymin",
            ymax="ymax",
            tooltip="tooltip",
            data_id="car_id",
            hover_key="car_id",
        ),
        fill="skyblue",
        color="white",
        size=0.35,
    )
    + gg.geom_point(
        data=scatter,
        mapping=gg.aes(
            x="x",
            y="y",
            tooltip="tooltip",
            data_id="car_id",
            hover_key="car_id",
        ),
        size=8,
        fill="#333333",
        color="#333333",
    )
    + gg.geom_segment(
        data=axis_segments,
        mapping=gg.aes(x="x", xend="xend", y="y", yend="yend"),
        color="#222222",
        size=0.35,
    )
    + gg.geom_segment(
        data=tick_segments,
        mapping=gg.aes(x="x", xend="xend", y="y", yend="yend"),
        color="#222222",
        size=0.35,
    )
    + gg.geom_text(
        data=scatter_x_ticks,
        mapping=gg.aes(x="x", y=-0.035, label="label"),
        size=12,
        va="top",
    )
    + gg.geom_text(
        data=scatter_y_ticks,
        mapping=gg.aes(x=-0.03, y="y", label="label"),
        size=12,
        ha="right",
    )
    + gg.geom_text(
        data=bar_x_ticks,
        mapping=gg.aes(x="x", y=-0.035, label="label"),
        size=12,
        va="top",
    )
    + gg.geom_text(
        data=bar,
        mapping=gg.aes(x=-0.02, y="y", label="carname"),
        size=8,
        ha="right",
    )
    + gg.geom_text(
        data=axis_labels,
        mapping=gg.aes(x="x", y="y", label="label", angle="angle"),
        size=10,
    )
    + gg.facet_wrap("view", nrow=1)
    + gg.coord_cartesian(xlim=(-0.25, 1.04), ylim=(-0.10, 1.08), expand=False)
    + gg.theme_void(base_size=10)
    + gg.theme(
        figure_size=(11, 7),
        plot_background=gg.element_rect(fill="white", color="white"),
        panel_background=gg.element_rect(fill="white", color="white"),
        strip_text=gg.element_text(size=12, weight="bold"),
        panel_spacing_x=0.08,
        plot_margin=0.02,
    )
)

(
    interactive(plot, hover_nearest=True)
    + css(".plot-element.hovered {fill: red; stroke: black;}")
    + save("docs/iframes/mtcars-linked-panels.html")
)
