import numpy as np
import pytest

from ninejs.main import _get_and_sanitize_js, _vector_to_list, css, save


def test_vector_to_list_accepts_common_iterables():
    assert _vector_to_list(["a", "b"]) == ["a", "b"]
    assert _vector_to_list(("a", "b")) == ["a", "b"]
    assert _vector_to_list(np.array(["a", "b"])) == ["a", "b"]


def test_vector_to_list_rejects_non_iterable_values():
    with pytest.raises(ValueError, match="labels"):
        _vector_to_list(1, name="labels")


def test_get_and_sanitize_js_returns_matching_content(tmp_path):
    js_file = tmp_path / "PlotParser.js"
    js_file.write_text("const ignored = true;\nclass PlotSVGParser {}\n")

    content = _get_and_sanitize_js(js_file, r"class PlotSVGParser.*")

    assert content == "class PlotSVGParser {}\n"


def test_get_and_sanitize_js_raises_when_pattern_is_missing(tmp_path):
    js_file = tmp_path / "PlotParser.js"
    js_file.write_text("const ignored = true;\n")

    with pytest.raises(ValueError, match="Could not find"):
        _get_and_sanitize_js(js_file, r"class PlotSVGParser.*")


def test_css_wrapper_accepts_string_dict_and_file(tmp_path):
    css_file = tmp_path / "style.css"
    css_file.write_text(".tooltip { color: red; }\n")

    assert css(".tooltip { color: red; }").css_content == ".tooltip { color: red; }"
    assert css(from_dict={".tooltip": {"color": "blue"}}).css_content == (
        ".tooltip{color:blue;}"
    )
    assert css(from_file=str(css_file)).css_content == ".tooltip { color: red; }\n"


def test_save_wrapper_stores_file_path():
    assert save("chart.html").file_path == "chart.html"
