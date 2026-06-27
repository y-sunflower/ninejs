import geopandas as gp
import pandas as pd
import plotnine as gg
from shapely.geometry import Polygon

from ninejs import css, interactive, save


palette = {
    "North": "#2f6f73",
    "Harbor": "#7a4e9f",
    "Market": "#d0643b",
    "Garden": "#4f8f47",
    "Station": "#c49a34",
}

regions = gp.GeoDataFrame(
    {
        "region": ["North", "Harbor", "Market", "Garden", "Station"],
        "value": [34, 27, 42, 19, 31],
        "geometry": [
            Polygon([(0, 2), (1.5, 2), (1.5, 3.2), (0, 3.2)]),
            Polygon([(1.5, 1.7), (3.0, 1.7), (3.0, 3.2), (1.5, 3.2)]),
            Polygon([(0.3, 0.7), (1.7, 0.7), (1.7, 2), (0.3, 2)]),
            Polygon([(1.7, 0.5), (3.2, 0.5), (3.2, 1.7), (1.7, 1.7)]),
            Polygon([(0.8, -0.2), (2.2, -0.2), (2.2, 0.7), (0.8, 0.7)]),
        ],
    },
    crs="EPSG:4326",
)
regions["tooltip"] = [
    f"{region}: {value} projects"
    for region, value in zip(regions["region"], regions["value"], strict=True)
]

bars = pd.DataFrame(regions.drop(columns="geometry")).sort_values("value")
bars["value_label"] = bars["value"].astype(str)

map_plot = (
    gg.ggplot()
    + gg.geom_map(
        data=regions,
        mapping=gg.aes(fill="region", tooltip="tooltip", hover_key="region"),
        color="white",
        size=1.2,
        alpha=0.95,
    )
    + gg.labs(title="District map")
    + gg.theme_void(base_size=10)
)

bar_plot = (
    gg.ggplot(bars, gg.aes("reorder(region, value)", "value"))
    + gg.geom_col(
        mapping=gg.aes(fill="region", tooltip="tooltip", hover_key="region"),
        width=0.72,
        alpha=0.95,
    )
    + gg.geom_text(gg.aes(y="value + 2.2", label="value_label"), size=8)
    + gg.labs(title="Project count", x="", y="")
    + gg.theme_void(base_size=10)
)

plot = (
    (map_plot | bar_plot) & gg.scale_fill_manual(values=palette, guide=None)
) & gg.theme(
    figure_size=(9.5, 4.8),
    plot_background=gg.element_rect(fill="#f7f4ef", color="#f7f4ef"),
    panel_background=gg.element_rect(fill="#f7f4ef", color="#f7f4ef"),
    plot_title=gg.element_text(size=12, weight="bold", color="#232323"),
    plot_margin=0.03,
)

(
    interactive(plot)
    + css(
        """
        .plot-element {
          transition: opacity 120ms ease, stroke-width 120ms ease;
        }
        .plot-element.hovered {
          stroke: #1d1d1d;
          stroke-width: 2.2px;
        }
        .plot-element.not-hovered {
          opacity: 0.22;
        }
        .tooltip {
          font-size: 14px;
        }
        """
    )
    + save("docs/iframes/linked-map-bars.html", minify=True)
)
