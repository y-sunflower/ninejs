import pytest

from ninejs.css import css_from_dict, css_from_file, is_css_like


def test_from_dict_serializes_css_rules():
    css = css_from_dict({".tooltip": {"color": "red", "font-size": "12px"}})
    assert css == ".tooltip{color:red;font-size:12px;}"


def test_from_file_reads_css(tmp_path):
    css_file = tmp_path / "style.css"
    css_file.write_text(".tooltip { color: red; }\n")
    assert css_from_file(str(css_file)) == ".tooltip { color: red; }\n"


@pytest.mark.parametrize(
    ("raw_css", "expected"),
    [
        (".tooltip { color: red; }", True),
        (".box { broken }", False),
        ("not css", False),
    ],
)
def test_is_css_like(raw_css, expected):
    assert is_css_like(raw_css) is expected
