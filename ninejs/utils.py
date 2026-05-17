import re
from typing import Any, Optional

import narwhals.stable.v2 as nw
from narwhals.stable.v2.dependencies import is_numpy_array, is_into_series
from plotnine import ggplot

from ninejs.const import (
    GROUPED_TOOLTIP_GEOM_KINDS,
    TOOLTIP_GEOM_KINDS,
    GEOM_KIND_BY_CLASS,
)


def _vector_to_list(vector, name="labels and groups") -> list:
    """
    Function used to easily convert various kind of iterables to
    lists in order to have standardised objects passed to javascript.

    It accepts all backend series from narwhals and common objects
    such as numpy arrays.

    Todo: test this extensively to make sure it behaves as expected.

    Args:
        vector: A valid iterable.
        name: The name passed to the error message when type is
            invalid.

    Returns:
        A list
    """
    if isinstance(vector, (list, tuple)) or is_numpy_array(vector):
        return list(vector)
    elif is_into_series(vector):
        return nw.from_native(vector, allow_series=True).to_list()
    else:
        raise ValueError(
            f"{name} must be a Series or a valid iterable (list, tuple, ndarray...)."
        )


def _get_and_sanitize_js(file_path, after_pattern):
    with open(file_path) as f:
        content = f.read()

    match = re.search(after_pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    else:
        raise ValueError(f"Could not find '{after_pattern}' in the file")


def _empty_tooltip_config() -> dict[str, list]:
    return {"tooltip_labels": [], "tooltip_groups": []}


def _empty_geom_tooltips() -> dict[str, dict[str, list]]:
    return {kind: _empty_tooltip_config() for kind in TOOLTIP_GEOM_KINDS}


def _normalize_tooltip_config(tooltip_config: Optional[dict]) -> dict[str, list]:
    if tooltip_config is None:
        return _empty_tooltip_config()

    return {
        "tooltip_labels": list(tooltip_config.get("tooltip_labels", [])),
        "tooltip_groups": list(tooltip_config.get("tooltip_groups", [])),
    }


def _normalize_geom_tooltips(
    geom_tooltips: Optional[dict[str, dict[str, list]]],
) -> dict[str, dict[str, list]]:
    normalized = _empty_geom_tooltips()

    if geom_tooltips is None:
        return normalized

    for geom_kind, tooltip_config in geom_tooltips.items():
        if geom_kind in normalized:
            normalized[geom_kind] = _normalize_tooltip_config(tooltip_config)

    return normalized


def _has_any_tooltip_config(geom_tooltips: dict[str, dict[str, list]]) -> bool:
    return any(
        tooltip_config["tooltip_labels"] or tooltip_config["tooltip_groups"]
        for tooltip_config in geom_tooltips.values()
    )


def _layer_geom_kind(layer: Any) -> Optional[str]:
    geom = getattr(layer, "geom", None)
    if geom is None:
        return None

    for cls in type(geom).mro():
        geom_kind = GEOM_KIND_BY_CLASS.get(cls.__name__)
        if geom_kind is not None:
            return geom_kind

    return None


def _get_built_layers(gg: ggplot):
    build_objs = getattr(gg, "_build_objs", None)
    layers = getattr(build_objs, "layers", None)
    if layers is not None:
        return layers

    return getattr(gg, "layers", [])


def _get_layer_data(layer: Any):
    return getattr(layer, "data", None)


def _first_values_by_group(data, column: str) -> list:
    values = data.groupby("group", sort=False)[column].first()
    return _vector_to_list(values, name=f"{column} values")


def _row_tooltip_config(data) -> dict[str, list]:
    labels = None
    groups = None

    if "tooltip" in data.columns:
        labels = _vector_to_list(data["tooltip"], name="tooltip labels")
    if "data_id" in data.columns:
        groups = _vector_to_list(data["data_id"], name="tooltip groups")

    if labels is None:
        labels = []
    if groups is None:
        groups = list(range(len(labels))) if labels else []

    return {"tooltip_labels": labels, "tooltip_groups": groups}


def _grouped_tooltip_config(data, geom_kind: str) -> dict[str, list]:
    if "group" not in data.columns:
        return _row_tooltip_config(data)

    if geom_kind == "lines":
        group_sizes = data.groupby("group", sort=False)["group"].transform("size")
        data = data[group_sizes >= 2]

    if len(data) == 0:
        return _empty_tooltip_config()

    labels = []
    groups = []

    if "tooltip" in data.columns:
        labels = _first_values_by_group(data, "tooltip")
    if "data_id" in data.columns:
        groups = _first_values_by_group(data, "data_id")

    if not groups and labels:
        groups = list(range(len(labels)))

    return {"tooltip_labels": labels, "tooltip_groups": groups}


def _layer_tooltip_config(layer: Any, geom_kind: str) -> dict[str, list]:
    data = _get_layer_data(layer)
    if data is None or not hasattr(data, "columns"):
        return _empty_tooltip_config()

    if "tooltip" not in data.columns and "data_id" not in data.columns:
        return _empty_tooltip_config()

    if geom_kind in GROUPED_TOOLTIP_GEOM_KINDS:
        return _grouped_tooltip_config(data, geom_kind)

    return _row_tooltip_config(data)


def _extend_tooltip_config(
    base: dict[str, list],
    extra: dict[str, list],
) -> None:
    base["tooltip_labels"].extend(extra["tooltip_labels"])
    base["tooltip_groups"].extend(extra["tooltip_groups"])


def _extract_geom_tooltips(gg: ggplot) -> Optional[dict[str, dict[str, list]]]:
    geom_tooltips = _empty_geom_tooltips()

    for layer in _get_built_layers(gg):
        geom_kind = _layer_geom_kind(layer)
        if geom_kind is None:
            continue

        tooltip_config = _layer_tooltip_config(layer, geom_kind)
        _extend_tooltip_config(geom_tooltips[geom_kind], tooltip_config)

    if not _has_any_tooltip_config(geom_tooltips):
        return None

    return geom_tooltips
