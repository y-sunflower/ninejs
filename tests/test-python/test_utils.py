from types import SimpleNamespace
from typing import cast

import pandas as pd
from plotnine import ggplot

from ninejs.utils import (
    _data_tooltip_config,
    _extract_geom_tooltips,
    _extract_panel_geom_tooltips,
    _get_built_layers,
    _get_js_bundle,
    _grouped_tooltip_config,
    _is_missing_value,
    _layer_geom_kind,
)


class geom_point:
    pass


def test_get_js_bundle_strips_trailing_source_map(tmp_path):
    bundle = tmp_path / "bundle.js"
    bundle.write_text(
        "console.log('loaded');\n//# sourceMappingURL=bundle.js.map\n",
        encoding="utf-8",
    )

    assert _get_js_bundle(bundle) == "console.log('loaded');"


def test_is_missing_value_handles_pd_na_and_uncomparable_values():
    class Uncomparable:
        def __ne__(self, other):
            raise TypeError("cannot compare")

    assert _is_missing_value(pd.NA) is True
    assert _is_missing_value(Uncomparable()) is False


def test_layer_geom_kind_ignores_missing_and_unknown_geoms():
    assert _layer_geom_kind(SimpleNamespace()) is None
    assert _layer_geom_kind(SimpleNamespace(geom=object())) is None


def test_get_built_layers_falls_back_to_gg_layers():
    gg = cast(ggplot, SimpleNamespace(layers=["fallback-layer"]))

    assert _get_built_layers(gg) == ["fallback-layer"]


def test_data_tooltip_config_handles_empty_inputs():
    assert _data_tooltip_config(None, "points") == {
        "tooltip_labels": [],
        "tooltip_groups": [],
        "hover_keys": [],
        "click_handlers": [],
    }
    assert _data_tooltip_config(object(), "points") == {
        "tooltip_labels": [],
        "tooltip_groups": [],
        "hover_keys": [],
        "click_handlers": [],
    }
    assert _data_tooltip_config(pd.DataFrame({"x": [1]}), "points") == {
        "tooltip_labels": [],
        "tooltip_groups": [],
        "hover_keys": [],
        "click_handlers": [],
    }


def test_data_tooltip_config_uses_hover_group():
    data = pd.DataFrame(
        {
            "tooltip": ["Alpha", "Beta"],
            "hover_group": ["new-a", "new-b"],
        }
    )

    assert _data_tooltip_config(data, "points") == {
        "tooltip_labels": ["Alpha", "Beta"],
        "tooltip_groups": ["new-a", "new-b"],
        "hover_keys": [],
        "click_handlers": [],
    }


def test_data_tooltip_config_accepts_hover_group_without_tooltip():
    data = pd.DataFrame({"hover_group": ["new-a", "new-b"]})

    assert _data_tooltip_config(data, "points") == {
        "tooltip_labels": [],
        "tooltip_groups": ["new-a", "new-b"],
        "hover_keys": [],
        "click_handlers": [],
    }


def test_data_tooltip_config_accepts_hover_key():
    data = pd.DataFrame(
        {
            "tooltip": ["Alpha", "Beta"],
            "hover_group": ["local-a", "local-b"],
            "hover_key": ["shared-a", "shared-b"],
        }
    )

    assert _data_tooltip_config(data, "points") == {
        "tooltip_labels": ["Alpha", "Beta"],
        "tooltip_groups": ["local-a", "local-b"],
        "hover_keys": ["shared-a", "shared-b"],
        "click_handlers": [],
    }


def test_data_tooltip_config_prefers_hover_group_over_data_id():
    data = pd.DataFrame(
        {
            "tooltip": ["Alpha", "Beta"],
            "hover_group": ["new-a", "new-b"],
            "data_id": ["old-a", "old-b"],
        }
    )

    assert _data_tooltip_config(data, "points") == {
        "tooltip_labels": ["Alpha", "Beta"],
        "tooltip_groups": ["new-a", "new-b"],
        "hover_keys": [],
        "click_handlers": [],
    }


def test_data_tooltip_config_keeps_data_id_without_warning(recwarn):
    data = pd.DataFrame(
        {
            "tooltip": ["Alpha", "Beta"],
            "data_id": ["old-a", "old-b"],
        }
    )

    assert _data_tooltip_config(data, "points") == {
        "tooltip_labels": ["Alpha", "Beta"],
        "tooltip_groups": ["old-a", "old-b"],
        "hover_keys": [],
        "click_handlers": [],
    }
    assert len(recwarn) == 0


def test_grouped_tooltip_config_falls_back_when_group_is_absent():
    data = pd.DataFrame({"tooltip": ["Alpha"], "on_click": ["globalThis.x = 1"]})

    assert _grouped_tooltip_config(data, "lines") == {
        "tooltip_labels": ["Alpha"],
        "tooltip_groups": [0],
        "hover_keys": [],
        "click_handlers": ["globalThis.x = 1"],
    }


def test_grouped_line_tooltip_config_drops_single_point_groups():
    data = pd.DataFrame({"group": [1, 2], "tooltip": ["Alpha", "Beta"]})

    assert _grouped_tooltip_config(data, "lines") == {
        "tooltip_labels": [],
        "tooltip_groups": [],
        "hover_keys": [],
        "click_handlers": [],
    }


def test_grouped_tooltip_config_defaults_groups_from_labels():
    data = pd.DataFrame(
        {
            "group": [2, 2, 1, 1],
            "tooltip": ["Beta", "Beta again", "Alpha", "Alpha again"],
        }
    )

    assert _grouped_tooltip_config(data, "areas") == {
        "tooltip_labels": ["Alpha", "Beta"],
        "tooltip_groups": [0, 1],
        "hover_keys": [],
        "click_handlers": [],
    }


def test_grouped_tooltip_config_prefers_hover_group_over_data_id():
    data = pd.DataFrame(
        {
            "group": [2, 2, 1, 1],
            "tooltip": ["Beta", "Beta again", "Alpha", "Alpha again"],
            "hover_group": ["new-b", "new-b", "new-a", "new-a"],
            "data_id": ["old-b", "old-b", "old-a", "old-a"],
        }
    )

    assert _grouped_tooltip_config(data, "areas") == {
        "tooltip_labels": ["Alpha", "Beta"],
        "tooltip_groups": ["new-a", "new-b"],
        "hover_keys": [],
        "click_handlers": [],
    }


def test_extract_panel_geom_tooltips_skips_unusable_layers():
    data = pd.DataFrame({"tooltip": ["Alpha"]})
    gg = cast(
        ggplot,
        SimpleNamespace(
            _build_objs=SimpleNamespace(
                layers=[
                    SimpleNamespace(),
                    SimpleNamespace(geom=geom_point(), data=None),
                    SimpleNamespace(geom=object(), data=data),
                ]
            )
        ),
    )

    assert _extract_panel_geom_tooltips(gg) is None
    assert _extract_geom_tooltips(gg) is None


def test_extract_panel_geom_tooltips_handles_non_panel_data():
    data = pd.DataFrame({"tooltip": ["Alpha", "Beta"]})
    gg = cast(
        ggplot,
        SimpleNamespace(
            _build_objs=SimpleNamespace(
                layers=[SimpleNamespace(geom=geom_point(), data=data)]
            )
        ),
    )

    panel_tooltips = _extract_panel_geom_tooltips(gg)

    assert panel_tooltips is not None
    assert panel_tooltips[1]["points"]["tooltip_labels"] == ["Alpha", "Beta"]
    assert panel_tooltips[1]["points"]["tooltip_groups"] == [0, 1]
