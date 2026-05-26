import pytest
from plotnine import aes, geom_point, ggplot, theme_minimal
from ninejs.data import anscombe_quartet

from ninejs.main import to_html
from ninejs.utils import _inline_style_to_presentation_attrs
import ninejs


def test_inline_style_promotes_allowlisted_props_to_attrs():
    svg = '<path d="M0 0" style="fill: red; stroke: blue; stroke-width: 2"/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="red"' in out
    assert 'stroke="blue"' in out
    assert 'stroke-width="2"' in out
    assert "style=" not in out


def test_inline_style_keeps_non_allowlisted_props_in_style():
    svg = '<text style="fill: red; font-family: Arial">hi</text>'
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="red"' in out
    assert 'style="font-family: Arial"' in out


def test_inline_style_handles_matplotlib_shape():
    svg = (
        '<path d="M0 0" '
        'style="fill: none; stroke-dasharray: 3.27904,1.417963; '
        "stroke-dashoffset: 0; stroke: #0d5c63; stroke-opacity: 0.4; "
        'stroke-width: 0.886227"/>'
    )
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="none"' in out
    assert 'stroke="#0d5c63"' in out
    assert 'stroke-opacity="0.4"' in out
    assert 'stroke-dasharray="3.27904,1.417963"' in out
    assert 'stroke-dashoffset="0"' in out
    assert 'stroke-width="0.886227"' in out
    assert "style=" not in out


def test_inline_style_leaves_other_attrs_intact():
    svg = '<circle cx="5" cy="5" r="3" style="fill: green"/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert 'cx="5"' in out
    assert 'cy="5"' in out
    assert 'r="3"' in out
    assert 'fill="green"' in out


def test_inline_style_empty_attr_is_removed():
    svg = '<path d="M0 0" style=""/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert "style=" not in out
    assert 'd="M0 0"' in out


def test_inline_style_handles_trailing_semicolon():
    svg = '<path style="fill: red;"/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="red"' in out
    assert "style=" not in out


def test_inline_style_handles_internal_extra_whitespace():
    svg = '<path style="  fill :   red ;   stroke:blue  "/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="red"' in out
    assert 'stroke="blue"' in out
    assert "style=" not in out


def test_inline_style_lowercases_property_name():
    svg = '<path style="FILL: red; Stroke-Width: 2"/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="red"' in out
    assert 'stroke-width="2"' in out


def test_inline_style_preserves_url_paint_value():
    svg = '<path style="fill: url(#gradient1)"/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="url(#gradient1)"' in out


@pytest.mark.parametrize(
    "value",
    ["none", "currentColor", "transparent", "#a1b2c3", "rgb(1, 2, 3)", "#000000"],
)
def test_inline_style_preserves_special_paint_values(value):
    svg = f'<path style="fill: {value}"/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert f'fill="{value}"' in out


def test_inline_style_transforms_multiple_elements_independently():
    svg = (
        "<g>"
        '<path style="fill: red"/>'
        '<circle style="stroke: blue; font-size: 12px"/>'
        '<rect style="fill: green"/>'
        "</g>"
    )
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="red"' in out
    assert 'stroke="blue"' in out
    assert 'style="font-size: 12px"' in out
    assert 'fill="green"' in out


def test_inline_style_is_idempotent():
    svg = '<path style="fill: red; stroke: blue; font-family: Arial" d="M0 0"/>'
    once = _inline_style_to_presentation_attrs(svg)
    twice = _inline_style_to_presentation_attrs(once)
    assert once == twice


def test_inline_style_no_op_when_no_style_attr():
    svg = '<path d="M0 0" stroke="red" fill="blue"/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert out == svg


def test_inline_style_preserves_surrounding_attribute_order():
    svg = '<path d="M0 0" style="fill: red" stroke-width="2"/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert out.index('d="M0 0"') < out.index('fill="red"')
    assert out.index('fill="red"') < out.index('stroke-width="2"')


def test_inline_style_only_non_allowlisted_keeps_style():
    svg = '<text style="font-family: Arial; font-size: 12px">hi</text>'
    out = _inline_style_to_presentation_attrs(svg)
    assert 'style="font-family: Arial; font-size: 12px"' in out


def test_inline_style_skips_malformed_declarations():
    svg = '<path style="fill: red; broken; stroke: blue"/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="red"' in out
    assert 'stroke="blue"' in out


def test_inline_style_ignores_consecutive_semicolons():
    svg = '<path style=";;fill: red;;"/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="red"' in out
    assert "style=" not in out


def test_inline_style_handles_newline_before_style_attr():
    svg = '<path\nstyle="fill: red"\nd="M0 0"/>'
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="red"' in out
    assert 'd="M0 0"' in out


def test_inline_style_promotes_all_allowlisted_props():
    decls = [
        ("fill", "red"),
        ("stroke", "blue"),
        ("stroke-width", "1.5"),
        ("stroke-linejoin", "round"),
        ("stroke-linecap", "butt"),
        ("stroke-miterlimit", "10"),
        ("stroke-opacity", "0.5"),
        ("stroke-dasharray", "4,2"),
        ("stroke-dashoffset", "0"),
        ("fill-opacity", "0.8"),
        ("opacity", "0.9"),
        ("color", "black"),
    ]
    style = "; ".join(f"{prop}: {value}" for prop, value in decls)
    svg = f'<path style="{style}"/>'
    out = _inline_style_to_presentation_attrs(svg)
    for prop, value in decls:
        assert f'{prop}="{value}"' in out
    assert "style=" not in out


def test_inline_style_does_not_touch_internal_style_element():
    svg = (
        "<svg>"
        '<defs><style type="text/css">*{stroke-linejoin:round}</style></defs>'
        '<path style="fill: red"/>'
        "</svg>"
    )
    out = _inline_style_to_presentation_attrs(svg)
    assert '<style type="text/css">*{stroke-linejoin:round}</style>' in out
    assert 'fill="red"' in out


def test_inline_style_combined_realistic_fragment():
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        "<g>"
        '<path style="fill: none; stroke: #000000; stroke-width: 0.886227"/>'
        '<circle cx="1" cy="2" r="3" '
        'style="fill: #e58606; stroke: #ffffff; font-family: Arial"/>'
        "</g></svg>"
    )
    out = _inline_style_to_presentation_attrs(svg)
    assert 'fill="none"' in out
    assert 'stroke="#000000"' in out
    assert 'stroke-width="0.886227"' in out
    assert 'cx="1"' in out
    assert 'fill="#e58606"' in out
    assert 'stroke="#ffffff"' in out
    assert 'style="font-family: Arial"' in out
    assert 'style="stroke' not in out
    assert 'style="fill' not in out


def test_to_html_strips_inline_style_from_matplotlib_svg():
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
        )
        + geom_point(size=4, alpha=0.7)
        + theme_minimal()
    )
    html = ninejs.interactive(gg) + to_html()
    assert 'style="stroke:' not in html
    assert 'style="fill:' not in html
