from __future__ import annotations

import json
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

    if type(value).__name__ == "NAType":
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


def _has_click_handler(click_handler: object) -> bool:
    if _is_missing_value(click_handler):
        return False

    return str(click_handler).strip() != ""


def _escape_js_script_content(javascript: str) -> str:
    return re.sub(
        r"</script",
        lambda match: "<\\/" + match.group(0)[2:],
        javascript,
        flags=re.IGNORECASE,
    )


def _indent_js_function_body(javascript: str) -> str:
    escaped = _escape_js_script_content(javascript)
    return "\n".join(f"    {line}" if line else "" for line in escaped.splitlines())


def _register_click_handler(
    click_handler: object,
    handler_ids_by_code: dict[str, str],
) -> str:
    click_handler_code = str(click_handler)
    if click_handler_code not in handler_ids_by_code:
        handler_ids_by_code[click_handler_code] = (
            f"ninejs_click_handler_{len(handler_ids_by_code)}"
        )

    return handler_ids_by_code[click_handler_code]


def _replace_click_handlers_with_ids(
    value: object,
    handler_ids_by_code: dict[str, str],
) -> None:
    if isinstance(value, list):
        for item in value:
            _replace_click_handlers_with_ids(item, handler_ids_by_code)
        return

    if not isinstance(value, dict):
        return

    data = cast(dict[str, object], value)
    for key, item in data.items():
        if key == "click_handlers" and isinstance(item, list):
            data[key] = [
                _register_click_handler(click_handler, handler_ids_by_code)
                if _has_click_handler(click_handler)
                else click_handler
                for click_handler in item
            ]
        else:
            _replace_click_handlers_with_ids(item, handler_ids_by_code)


def _extract_click_handler_javascript(plot_data_json: dict[str, object]) -> str:
    handler_ids_by_code: dict[str, str] = {}
    _replace_click_handlers_with_ids(plot_data_json, handler_ids_by_code)

    if not handler_ids_by_code:
        return ""

    handler_definitions = []
    for click_handler_code, handler_id in handler_ids_by_code.items():
        handler_definitions.append(
            f"  {json.dumps(handler_id)}: function(event) {{\n"
            f"{_indent_js_function_body(click_handler_code)}\n"
            "  }"
        )

    return (
        "globalThis.ninejs = globalThis.ninejs || {};\n"
        "globalThis.ninejs.clickHandlers = "
        "globalThis.ninejs.clickHandlers || {};\n"
        "Object.assign(globalThis.ninejs.clickHandlers, {\n"
        + ",\n".join(handler_definitions)
        + "\n});"
    )


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
    geom_tooltips: Mapping[str, Mapping[str, Iterable[object]]],
) -> GeomTooltips:
    normalized = _empty_geom_tooltips()

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
    # Sort by group key (ascending) so the order matches the SVG path
    # order matplotlib emits — `<g id="FillBetweenPolyCollection_N">`
    # elements are always written in ascending group-ID order, even when
    # a group is missing at the earliest x values.
    values = data.groupby("group", sort=True)[column].first()
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


def _layer_tooltip_config(layer: object, geom_kind: str) -> TooltipConfig:
    data = _get_layer_data(layer)
    return _data_tooltip_config(data, geom_kind)


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
            _extend_tooltip_config(
                panel_geom_tooltips[panel][geom_kind], tooltip_config
            )

    if not any(
        _has_any_tooltip_config(geom_tooltips)
        for geom_tooltips in panel_geom_tooltips.values()
    ):
        return None

    return panel_geom_tooltips
