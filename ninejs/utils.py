from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from typing import Any, Optional, cast

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


def _inline_style_to_presentation_attrs(svg: str) -> str:
    """
    TLDR: transforms each style attribute:
    Before: <path d="M0 0 L10 10" style="fill: none; stroke: #0d5c63; stroke-width: 0.886; stroke-opacity: 0.4"/>

    After:
    <path d="M0 0 L10 10" fill="none" stroke="#0d5c63" stroke-width="0.886" stroke-opacity="0.4"/>

    Promote inline `style="prop: value; ..."` declarations on SVG
    elements to standalone presentation attributes (e.g. `stroke="..."`,
    `fill="..."`) when the property is in the allowlist.

    Presentation attributes sit below author CSS in the cascade, so this
    lets user-supplied CSS override matplotlib's defaults without
    `!important`. Properties outside the allowlist are kept inside a
    reduced `style="..."` attribute.

    Original issue: https://github.com/y-sunflower/ninejs/issues/71
    """

    PRESENTATION_ATTR_ALLOWLIST: frozenset[str] = frozenset(
        {
            "fill",
            "stroke",
            "stroke-width",
            "stroke-linejoin",
            "stroke-linecap",
            "stroke-miterlimit",
            "stroke-opacity",
            "stroke-dasharray",
            "stroke-dashoffset",
            "fill-opacity",
            "opacity",
            "color",
        }
    )

    def replace(match: re.Match[str]) -> str:
        whitespace = match.group(1)
        promoted: list[str] = []
        leftover: list[str] = []
        for decl in match.group(2).split(";"):
            decl = decl.strip()
            if not decl or ":" not in decl:
                continue
            prop, _, value = decl.partition(":")
            prop = prop.strip().lower()
            value = value.strip()
            if prop in PRESENTATION_ATTR_ALLOWLIST:
                promoted.append(f'{prop}="{value}"')
            else:
                leftover.append(f"{prop}: {value}")
        attrs = list(promoted)
        if leftover:
            attrs.append(f'style="{"; ".join(leftover)}"')
        if not attrs:
            return whitespace
        return whitespace + " ".join(attrs)

    return re.compile(r'(\s)style="([^"]*)"').sub(replace, svg)


def _strip_js_module_syntax(content: str) -> str:
    content = re.sub(r"^\s*import\b[\s\S]*?;\s*", "", content, flags=re.MULTILINE)
    content = re.sub(r"\bexport\s+default\s+", "", content)
    content = re.sub(r"\bexport\s+", "", content)
    return content.strip()


def _get_js_module_bundle(file_paths: Iterable[Pathish]) -> str:
    modules: list[str] = []
    for file_path in file_paths:
        with open(file_path, encoding="utf-8") as f:
            modules.append(_strip_js_module_syntax(f.read()))

    return "\n\n".join(modules) + "\n"


def _get_js_bundle(file_path: Pathish) -> str:
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    return re.sub(r"\n?//# sourceMappingURL=.*\n?\Z", "", content)


def _empty_tooltip_config() -> TooltipConfig:
    return {
        "tooltip_labels": [],
        "tooltip_groups": [],
        "hover_keys": [],
        "click_handlers": [],
    }


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


def _repeat_exact(values: list[object], length: int) -> list[object]:
    if len(values) == 0 or len(values) == length:
        return values

    if length > len(values) and length % len(values) == 0:
        return [values[i % len(values)] for i in range(length)]

    return values


def _complete_tooltip_config(
    *,
    labels: Optional[list[object]] = None,
    groups: Optional[list[object]] = None,
    hover_keys: Optional[list[object]] = None,
    click_handlers: Optional[list[object]] = None,
    length: Optional[int] = None,
) -> TooltipConfig:
    labels = [] if labels is None else labels
    groups = [] if groups is None else groups
    hover_keys = [] if hover_keys is None else hover_keys
    click_handlers = [] if click_handlers is None else click_handlers

    if length is None:
        length = max(
            len(labels),
            len(groups),
            len(hover_keys),
            len(click_handlers),
            0,
        )

    labels = _repeat_exact(labels, length)
    groups = _repeat_exact(groups, length)
    hover_keys = _repeat_exact(hover_keys, length)
    click_handlers = _repeat_exact(click_handlers, length)

    if not groups and (labels or click_handlers):
        groups = list(range(length))

    return {
        "tooltip_labels": labels,
        "tooltip_groups": groups,
        "hover_keys": hover_keys,
        "click_handlers": click_handlers,
    }


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


def _normalize_tooltip_config(
    tooltip_config: Optional[Mapping[str, Iterable[object]]],
) -> TooltipConfig:
    if tooltip_config is None:
        return _empty_tooltip_config()

    return _complete_tooltip_config(
        labels=list(tooltip_config.get("tooltip_labels", [])),
        groups=list(tooltip_config.get("tooltip_groups", [])),
        hover_keys=list(tooltip_config.get("hover_keys", [])),
        click_handlers=_normalize_click_handlers(
            tooltip_config.get("click_handlers", [])
        ),
    )


def _normalize_geom_tooltips(
    geom_tooltips: Mapping[str, Mapping[str, Iterable[object]]],
) -> GeomTooltips:
    # Only emit the geom kinds that are actually configured: absent kinds
    # fall back to the axes-level tooltip config browser-side.
    return {
        geom_kind: _normalize_tooltip_config(tooltip_config)
        for geom_kind, tooltip_config in geom_tooltips.items()
        if geom_kind in TOOLTIP_GEOM_KINDS
    }


def _has_any_tooltip_config(geom_tooltips: GeomTooltips) -> bool:
    return any(
        tooltip_config["tooltip_labels"]
        or tooltip_config["tooltip_groups"]
        or tooltip_config["hover_keys"]
        or tooltip_config["click_handlers"]
        for tooltip_config in geom_tooltips.values()
    )


def _layer_geom_kind(layer: object) -> Optional[str]:
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


def _get_layer_data(layer: object) -> Optional[Any]:
    return getattr(layer, "data", None)


def _first_values_by_group(data: Any, column: str) -> list[object]:
    # Sort by group key (ascending) so the order matches the SVG path
    # order matplotlib emits — `<g id="FillBetweenPolyCollection_N">`
    # elements are always written in ascending group-ID order, even when
    # a group is missing at the earliest x values.
    values = data.groupby("group", sort=True)[column].first()
    return _vector_to_list(values, name=f"{column} values")


def _tooltip_group_column(data: Any) -> Optional[str]:
    if "hover_group" in data.columns:
        return "hover_group"
    if "data_id" in data.columns:
        return "data_id"
    return None


def _has_interactive_config(data: Any) -> bool:
    return (
        "tooltip" in data.columns
        or _tooltip_group_column(data) is not None
        or "hover_key" in data.columns
        or "on_click" in data.columns
    )


def _row_tooltip_config(data: Any) -> TooltipConfig:
    labels: Optional[list[object]] = None
    groups: Optional[list[object]] = None
    hover_keys: Optional[list[object]] = None
    click_handlers: Optional[list[object]] = None
    group_column = _tooltip_group_column(data)

    if "tooltip" in data.columns:
        labels = _vector_to_list(data["tooltip"], name="tooltip labels")
    if group_column is not None:
        groups = _vector_to_list(data[group_column], name="tooltip groups")
    if "hover_key" in data.columns:
        hover_keys = _vector_to_list(data["hover_key"], name="hover keys")
    if "on_click" in data.columns:
        click_handlers = _normalize_click_handlers(
            _vector_to_list(data["on_click"], name="click handlers")
        )

    return _complete_tooltip_config(
        labels=labels,
        groups=groups,
        hover_keys=hover_keys,
        click_handlers=click_handlers,
        length=len(data),
    )


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
    hover_keys: list[object] = []
    click_handlers: list[object] = []
    group_column = _tooltip_group_column(data)

    if "tooltip" in data.columns:
        labels = _first_values_by_group(data, "tooltip")
    if group_column is not None:
        groups = _first_values_by_group(data, group_column)
    if "hover_key" in data.columns:
        hover_keys = _first_values_by_group(data, "hover_key")
    if "on_click" in data.columns:
        click_handlers = _normalize_click_handlers(
            _first_values_by_group(data, "on_click")
        )

    return _complete_tooltip_config(
        labels=labels,
        groups=groups,
        hover_keys=hover_keys,
        click_handlers=click_handlers,
        length=len(data["group"].drop_duplicates()),
    )


def _data_tooltip_config(data: Any, geom_kind: str) -> TooltipConfig:
    if data is None or not hasattr(data, "columns"):
        return _empty_tooltip_config()

    if not _has_interactive_config(data):
        return _empty_tooltip_config()

    if geom_kind in GROUPED_TOOLTIP_GEOM_KINDS:
        return _grouped_tooltip_config(data, geom_kind)

    return _row_tooltip_config(data)


def _extend_tooltip_config(
    base: TooltipConfig,
    extra: TooltipConfig,
) -> None:
    base["tooltip_labels"].extend(extra["tooltip_labels"])
    base["tooltip_groups"].extend(extra["tooltip_groups"])
    base["hover_keys"].extend(extra["hover_keys"])
    base["click_handlers"].extend(extra["click_handlers"])


def _extract_panel_geom_tooltips(
    gg: ggplot,
) -> Optional[PanelGeomTooltips]:
    panel_geom_tooltips: PanelGeomTooltips = {}

    for layer in _get_built_layers(gg):
        geom_kind = _layer_geom_kind(layer)
        if geom_kind is None:
            continue

        data = _get_layer_data(layer)
        if data is None or not hasattr(data, "columns"):
            continue

        if not _has_interactive_config(data):
            continue

        if "PANEL" in data.columns:
            panel_items = data.groupby("PANEL", sort=False)
        else:
            panel_items = [(1, data)]

        for panel, panel_data in panel_items:
            panel = int(panel)

            geom_tooltips = panel_geom_tooltips.setdefault(panel, {})
            tooltip_config = _data_tooltip_config(panel_data, geom_kind)
            _extend_tooltip_config(
                geom_tooltips.setdefault(geom_kind, _empty_tooltip_config()),
                tooltip_config,
            )

    if not any(
        _has_any_tooltip_config(geom_tooltips)
        for geom_tooltips in panel_geom_tooltips.values()
    ):
        return None

    return panel_geom_tooltips


def _extract_geom_tooltips(gg: ggplot) -> Optional[GeomTooltips]:
    panel_geom_tooltips = _extract_panel_geom_tooltips(gg)
    if panel_geom_tooltips is None:
        return None

    merged: GeomTooltips = {}
    for geom_tooltips in panel_geom_tooltips.values():
        for geom_kind, tooltip_config in geom_tooltips.items():
            _extend_tooltip_config(
                merged.setdefault(geom_kind, _empty_tooltip_config()),
                tooltip_config,
            )

    return merged if _has_any_tooltip_config(merged) else None
