from __future__ import annotations

from typing import Final

# All the different kind of visual elements. Those elements
# are mapped (below) to one or multiple geoms.
TOOLTIP_GEOM_KINDS: Final[tuple[str, ...]] = (
    "points",
    "lines",
    "bars",
    "boxes",
    "areas",
    "polygons",
)

# For each geom, we need to say to what kind of visual
# element it is mapped in order to know how to parse it on the
# JS side (e.g., geom_point is the "same" as geom_jitter).
GEOM_KIND_BY_CLASS: Final[dict[str, str]] = {
    "geom_point": "points",
    "geom_jitter": "points",
    "geom_line": "lines",
    "geom_path": "lines",
    "geom_step": "lines",
    "geom_bar": "bars",
    "geom_col": "bars",
    "geom_histogram": "bars",
    "geom_boxplot": "boxes",
    "geom_rect": "bars",
    "geom_area": "areas",
    "geom_ribbon": "areas",
    "geom_map": "polygons",
}

# Those elements are "grouped": one line/area gets one
# tooltip label
GROUPED_TOOLTIP_GEOM_KINDS: Final[set[str]] = {"lines", "areas"}
