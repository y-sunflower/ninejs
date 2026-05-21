import geopandas as gp
import geodatasets
from plotnine import (
    ggplot,
    aes,
    coord_fixed,
    geom_map,
    geom_text,
    scale_fill_continuous,
    stage,
    element_line,
    element_rect,
    element_text,
    theme_void,
    theme,
)
from ninejs import interactive, save


def good_centroid(geometry):
    """
    Calculate "good" centroids for polygons in the geometry

    The polygon is projected onto the Equal Area Cylindrical projection,
    the centroids are computed, then mapped back onto the original
    coordinate system.
    """
    return geometry.to_crs("+proj=cea").centroid.to_crs(geometry.crs)


def overlay_color(rgb_hex_colors, light="white", dark="black", threshold=0.5):
    """
    Decide which color is suitable to write onto the given colors
    """

    def luminance(rgb_hex):
        """
        Calculate the Luminance ([0, 1]) of a hex color
        """
        r = int(rgb_hex[1:3], 16)
        g = int(rgb_hex[3:5], 16)
        b = int(rgb_hex[5:], 16)
        luma = (r * 0.299 + g * 0.587 + b * 0.0722) / 256
        return luma

    return [light if luminance(x) < threshold else dark for x in rgb_hex_colors]


geodatasets.fetch("geoda sids")
sids = gp.read_file(geodatasets.get_path("geoda.sids"))
data = sids.copy()

# Calculate the death per 1000
data["1974 - 1978"] = (data["SID74"] / data["BIR74"]) * 1000
data["1979 - 1984"] = (data["SID79"] / data["BIR79"]) * 1000

# Calculate center coordinates for the counties
data["center_lon"] = good_centroid(data.geometry).x
data["center_lat"] = good_centroid(data.geometry).y

# Make the data
data = data.melt(
    id_vars=["NAME", "geometry", "center_lon", "center_lat"],
    value_vars=["1974 - 1978", "1979 - 1984"],
    var_name="period",
    value_name="deaths_per_1k",
).rename({"NAME": "county"}, axis=1)

plot = (
    ggplot(data)
    + geom_map(aes(fill="deaths_per_1k", tooltip="deaths_per_1k"))
    + geom_text(
        aes(
            "center_lon",
            "center_lat",
            label="county",
            color=stage("deaths_per_1k", after_scale="overlay_color(color)"),
        ),
        size=6,
        show_legend=False,
    )
    + scale_fill_continuous(
        name="Deaths Per 1000",
        cmap_name="plasma",
        breaks=[0, 2.5, 5, 7.5, 10],
        labels=["0", "2.5", "5", "7.5", "10"],
        limits=[0, 10],
    )
    + coord_fixed(expand=False)
    + theme_void()
    + theme(
        figure_size=(12, 8),
        legend_position=(0, 0),
        legend_direction="horizontal",
        legend_title_position="top",
        plot_margin=0.01,
        plot_background=element_rect(fill="white"),
        panel_spacing=0.025,
        legend_frame=element_rect(color="black"),
        legend_ticks=element_line(color="black"),
        strip_text=element_text(size=12),
    )
)
plot.draw().savefig("debug.svg")

interactive(plot) + save("docs/iframes/choropleth.html", minify=True)
