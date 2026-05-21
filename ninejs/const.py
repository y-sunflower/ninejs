from __future__ import annotations

from typing import Final

TOOLTIP_GEOM_KINDS: Final[tuple[str, ...]] = (
    "points",
    "lines",
    "bars",
    "areas",
    "polygons",
)

GEOM_KIND_BY_CLASS: Final[dict[str, str]] = {
    "geom_point": "points",
    "geom_jitter": "points",
    "geom_line": "lines",
    "geom_path": "lines",
    "geom_step": "lines",
    "geom_bar": "bars",
    "geom_col": "bars",
    "geom_histogram": "bars",
    "geom_area": "areas",
    "geom_ribbon": "areas",
    "geom_map": "polygons",
}

GROUPED_TOOLTIP_GEOM_KINDS: Final[set[str]] = {"lines", "areas"}
