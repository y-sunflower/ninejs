from __future__ import annotations

from collections.abc import Sequence
from os import PathLike
from typing import Any, TypeAlias

from narwhals.typing import IntoSeries
from numpy.typing import NDArray
from plotnine import ggplot

try:
    from plotnine.composition import Compose
except ImportError:  # pragma: no cover - compatibility with older plotnine
    Compose = Any  # type: ignore

ArrayLike: TypeAlias = Sequence[object] | NDArray[Any] | IntoSeries
Pathish: TypeAlias = str | PathLike[str]
PlotnineChart: TypeAlias = ggplot | Compose
TooltipConfig: TypeAlias = dict[str, list[object]]
GeomTooltips: TypeAlias = dict[str, TooltipConfig]
PanelGeomTooltips: TypeAlias = dict[int, GeomTooltips]
