from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any, cast

import narwhals.stable.v2 as nw
from narwhals.stable.v2.dependencies import is_numpy_array, is_into_series
from plotnine import ggplot

from ninejs.const import (
    GROUPED_TOOLTIP_GEOM_KINDS,
    TOOLTIP_GEOM_KINDS,
    GEOM_KIND_BY_CLASS,
)
from ninejs.typing import GeomTooltips, PanelGeomTooltips, TooltipConfig, Pathish


def _vector_to_list(vector: object, name: str = "labels and groups") -> list[object]:
    """
    Function used to easily convert various kinds of iterables to
    lists in order to pass standardized objects to JavaScript.

    It accepts all backend series from narwhals and common objects
    such as numpy arrays.

    TODO: Test this extensively to make sure it behaves as expected.

    Args:
        vector: A valid iterable.
        name: The name passed to the error message when type is
            invalid.

    Returns:
        A list.
    """
    if isinstance(vector, (list, tuple)) or is_numpy_array(vector):
        return list(cast(Iterable[object], vector))
    elif is_into_series(vector):
        return list(
            cast(Iterable[object], nw.from_native(vector, allow_series=True).to_list())
        )
    else:
        raise ValueError(
            f"{name} must be a Series or a valid iterable (list, tuple, ndarray...)."
        )


def _get_and_sanitize_js(file_path: Pathish, after_pattern: str) -> str:
    with open(file_path) as f:
        content = f.read()

    match = re.search(after_pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    else:
        raise ValueError(f"Could not find '{after_pattern}' in the file")


def _strip_js_module_syntax(content: str) -> str:
    content = re.sub(r"^\s*import\b[\s\S]*?;\s*", "", content, flags=re.MULTILINE)
    content = re.sub(r"\bexport\s+default\s+", "", content)
    content = re.sub(r"\bexport\s+", "", content)
    return content.strip()


def _get_js_module_bundle(file_paths: Iterable[Pathish]) -> str:
    modules: list[str] = []
    for file_path in file_paths:
        with open(file_path) as f:
            modules.append(_strip_js_module_syntax(f.read()))

    return "\n\n".join(modules) + "\n"


def _get_js_bundle(file_path: Pathish) -> str:
    with open(file_path) as f:
        content = f.read()

    return re.sub(r"\n?//# sourceMappingURL=.*\n?\Z", "", content)


def _empty_tooltip_config() -> TooltipConfig:
    return {"tooltip_labels": [], "tooltip_groups": [], "click_handlers": []}


def _is_missing_value(value: object) -> bool:
    if value is None:
        return True

    try:
        return value != value
    except (TypeError, ValueError):
        return False


def _normalize_click_handlers(click_handlers: Iterable[object]) -> list[object]:
    return [
        None if _is_missing_value(click_handler) else click_handler
        for click_handler in click_handlers
    ]


def _empty_geom_tooltips() -> GeomTooltips:
    return {kind: _empty_tooltip_config() for kind in TOOLTIP_GEOM_KINDS}


def _normalize_tooltip_config(
    tooltip_config: Mapping[str, Iterable[object]] | None,
) -> TooltipConfig:
    if tooltip_config is None:
        return _empty_tooltip_config()

    return {
        "tooltip_labels": list(tooltip_config.get("tooltip_labels", [])),
        "tooltip_groups": list(tooltip_config.get("tooltip_groups", [])),
        "click_handlers": _normalize_click_handlers(
            tooltip_config.get("click_handlers", [])
        ),
    }


def _normalize_geom_tooltips(
    geom_tooltips: Mapping[str, Mapping[str, Iterable[object]]] | None,
) -> GeomTooltips:
    normalized = _empty_geom_tooltips()

    if geom_tooltips is None:
        return normalized

    for geom_kind, tooltip_config in geom_tooltips.items():
        if geom_kind in normalized:
            normalized[geom_kind] = _normalize_tooltip_config(tooltip_config)

    return normalized


def _has_any_tooltip_config(geom_tooltips: GeomTooltips) -> bool:
    return any(
        tooltip_config["tooltip_labels"]
        or tooltip_config["tooltip_groups"]
        or tooltip_config["click_handlers"]
        for tooltip_config in geom_tooltips.values()
    )


def _layer_geom_kind(layer: object) -> str | None:
    geom = getattr(layer, "geom", None)
    if geom is None:
        return None

    for cls in type(geom).mro():
        geom_kind = GEOM_KIND_BY_CLASS.get(cls.__name__)
        if geom_kind is not None:
            return geom_kind

    return None


def _get_built_layers(gg: ggplot) -> Iterable[object]:
    build_objs = getattr(gg, "_build_objs", None)
    layers = getattr(build_objs, "layers", None)
    if layers is not None:
        return layers

    return getattr(gg, "layers", [])


def _get_layer_data(layer: object) -> Any | None:
    return getattr(layer, "data", None)


def _first_values_by_group(data: Any, column: str) -> list[object]:
    values = data.groupby("group", sort=False)[column].first()
    return _vector_to_list(values, name=f"{column} values")


def _row_tooltip_config(data: Any) -> TooltipConfig:
    labels: list[object] | None = None
    groups: list[object] | None = None
    click_handlers: list[object] | None = None

    if "tooltip" in data.columns:
        labels = _vector_to_list(data["tooltip"], name="tooltip labels")
    if "data_id" in data.columns:
        groups = _vector_to_list(data["data_id"], name="tooltip groups")
    if "on_click" in data.columns:
        click_handlers = _normalize_click_handlers(
            _vector_to_list(data["on_click"], name="click handlers")
        )

    if labels is None:
        labels = []
    if click_handlers is None:
        click_handlers = []
    if groups is None:
        groups = list(range(len(labels))) if labels else []

    return {
        "tooltip_labels": labels,
        "tooltip_groups": groups,
        "click_handlers": click_handlers,
    }


def _grouped_tooltip_config(data: Any, geom_kind: str) -> TooltipConfig:
    if "group" not in data.columns:
        return _row_tooltip_config(data)

    if geom_kind == "lines":
        group_sizes = data.groupby("group", sort=False)["group"].transform("size")
        data = data[group_sizes >= 2]

    if len(data) == 0:
        return _empty_tooltip_config()

    labels: list[object] = []
    groups: list[object] = []
    click_handlers: list[object] = []

    if "tooltip" in data.columns:
        labels = _first_values_by_group(data, "tooltip")
    if "data_id" in data.columns:
        groups = _first_values_by_group(data, "data_id")
    if "on_click" in data.columns:
        click_handlers = _normalize_click_handlers(
            _first_values_by_group(data, "on_click")
        )

    if not groups:
        groups = list(range(len(labels))) if labels else []

    return {
        "tooltip_labels": labels,
        "tooltip_groups": groups,
        "click_handlers": click_handlers,
    }


def _data_tooltip_config(data: Any, geom_kind: str) -> TooltipConfig:
    if data is None or not hasattr(data, "columns"):
        return _empty_tooltip_config()

    if (
        "tooltip" not in data.columns
        and "data_id" not in data.columns
        and "on_click" not in data.columns
    ):
        return _empty_tooltip_config()

    if geom_kind in GROUPED_TOOLTIP_GEOM_KINDS:
        return _grouped_tooltip_config(data, geom_kind)

    return _row_tooltip_config(data)


def _reverse_tooltip_config(tooltip_config: TooltipConfig) -> TooltipConfig:
    return {
        "tooltip_labels": list(reversed(tooltip_config["tooltip_labels"])),
        "tooltip_groups": list(reversed(tooltip_config["tooltip_groups"])),
        "click_handlers": list(reversed(tooltip_config["click_handlers"])),
    }


# Areas are a special case.
# https://github.com/y-sunflower/ninejs/issues/39
def _should_reverse_area_tooltip_config(layer: object, geom_kind: str) -> bool:
    if geom_kind != "areas":
        return False

    position = getattr(layer, "position", None)
    if type(position).__name__ not in {"position_fill", "position_stack"}:
        return False

    params = getattr(position, "params", {}) or {}
    return not bool(params.get("reverse", False))


def _order_layer_tooltip_config(
    layer: object,
    geom_kind: str,
    tooltip_config: TooltipConfig,
) -> TooltipConfig:
    if _should_reverse_area_tooltip_config(layer, geom_kind):
        return _reverse_tooltip_config(tooltip_config)

    return tooltip_config


def _layer_tooltip_config(layer: object, geom_kind: str) -> TooltipConfig:
    data = _get_layer_data(layer)
    tooltip_config = _data_tooltip_config(data, geom_kind)
    return _order_layer_tooltip_config(layer, geom_kind, tooltip_config)


def _extend_tooltip_config(
    base: TooltipConfig,
    extra: TooltipConfig,
) -> None:
    base["tooltip_labels"].extend(extra["tooltip_labels"])
    base["tooltip_groups"].extend(extra["tooltip_groups"])
    base["click_handlers"].extend(extra["click_handlers"])


def _extract_geom_tooltips(gg: ggplot) -> GeomTooltips | None:
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


def _extract_panel_geom_tooltips(
    gg: ggplot,
) -> PanelGeomTooltips | None:
    panel_geom_tooltips: PanelGeomTooltips = {}

    for layer in _get_built_layers(gg):
        geom_kind = _layer_geom_kind(layer)
        if geom_kind is None:
            continue

        data = _get_layer_data(layer)
        if data is None or not hasattr(data, "columns"):
            continue

        if (
            "tooltip" not in data.columns
            and "data_id" not in data.columns
            and "on_click" not in data.columns
        ):
            continue

        if "PANEL" in data.columns:
            panel_items = data.groupby("PANEL", sort=False)
        else:
            panel_items = [(1, data)]

        for panel, panel_data in panel_items:
            panel = int(panel)

            if panel not in panel_geom_tooltips:
                panel_geom_tooltips[panel] = _empty_geom_tooltips()

            tooltip_config = _data_tooltip_config(panel_data, geom_kind)
            tooltip_config = _order_layer_tooltip_config(
                layer, geom_kind, tooltip_config
            )
            _extend_tooltip_config(
                panel_geom_tooltips[panel][geom_kind], tooltip_config
            )

    if not any(
        _has_any_tooltip_config(geom_tooltips)
        for geom_tooltips in panel_geom_tooltips.values()
    ):
        return None

    return panel_geom_tooltips
