import pytest

from ninejs.css import css_from_dict, css_from_file, is_css_like
import ninejs
from plotnine import ggplot, aes, geom_point, theme_minimal

from ninejs.data import anscombe_quartet


def test_from_dict_serializes_css_rules():
    css = css_from_dict({".tooltip": {"color": "red", "font-size": "12px"}})
    assert css == ".tooltip{color:red;font-size:12px;}"


def test_from_dict_warns_for_invalid_css():
    with pytest.warns(UserWarning, match="CSS may be invalid"):
        css = css_from_dict({".tooltip": {"broken": ""}})

    assert css == ".tooltip{broken:;}"


def test_from_file_reads_css(tmp_path):
    css_file = tmp_path / "style.css"
    css_file.write_text(".tooltip { color: red; }\n")
    assert css_from_file(str(css_file)) == ".tooltip { color: red; }\n"


def test_from_file_warns_for_invalid_css(tmp_path):
    css_file = tmp_path / "style.css"
    css_file.write_text("not css")

    with pytest.warns(UserWarning, match="CSS may be invalid"):
        assert css_from_file(str(css_file)) == "not css"


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


def test_adding_css_actually_adds_css():
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
        )
        + geom_point(size=4, alpha=0.7)
        + theme_minimal()
    )

    ip = ninejs.interactive(gg) + ninejs.css(".tooltip: {color: red;}")
    assert ip.plot.additional_css == ".tooltip: {color: red;}"

    ip = ip + ninejs.css(".tooltip: {font-weight: bold;")
    assert (
        ip.plot.additional_css == ".tooltip: {color: red;}.tooltip: {font-weight: bold;"
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"from_string": ".tooltip { color: red; }", "from_dict": {".x": {"y": "z"}}},
        {"from_string": ".tooltip { color: red; }", "from_file": "style.css"},
    ],
)
def test_css_requires_exactly_one_source(kwargs):
    with pytest.raises(ValueError, match="Exactly one"):
        ninejs.css(**kwargs)
