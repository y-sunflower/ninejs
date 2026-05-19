from __future__ import annotations

from collections.abc import Sequence
from os import PathLike
from typing import Any, TypeAlias

from narwhals.typing import IntoSeries
from numpy.typing import NDArray

ArrayLike: TypeAlias = Sequence[object] | NDArray[Any] | IntoSeries
Pathish: TypeAlias = str | PathLike[str]
TooltipConfig: TypeAlias = dict[str, list[object]]
GeomTooltips: TypeAlias = dict[str, TooltipConfig]
PanelGeomTooltips: TypeAlias = dict[int, GeomTooltips]
