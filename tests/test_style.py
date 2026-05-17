import pytest

from ninejs import style


def test_from_dict_serializes_css_rules():
    css = style.from_dict(
        {
            ".tooltip": {
                "color": "red",
                "font-size": "12px",
            }
        }
    )

    assert css == ".tooltip{color:red;font-size:12px;}"


def test_from_file_reads_css(tmp_path):
    css_file = tmp_path / "style.css"
    css_file.write_text(".tooltip { color: red; }\n")

    assert style.from_file(str(css_file)) == ".tooltip { color: red; }\n"


@pytest.mark.parametrize(
    ("raw_css", "expected"),
    [
        (".tooltip { color: red; }", True),
        (".box { broken }", False),
        ("not css", False),
    ],
)
def test_is_css_like(raw_css, expected):
    assert style.is_css_like(raw_css) is expected
