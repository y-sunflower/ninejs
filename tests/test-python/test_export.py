import os
import re
from html import unescape

from plotnine import aes, geom_point, ggplot
from ninejs.data import anscombe_quartet

import ninejs.main as main_module
from ninejs.main import css, interactive, javascript, save, show, to_html, to_iframe


def test_save_wrapper_stores_file_path():
    default_save = save("chart.html")
    minified_save = save("chart.html", minify=False)

    assert default_save.file_path == "chart.html"
    assert default_save.minify is True
    assert minified_save.minify is False


def test_to_html_can_minify_output():
    gg = (
        ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", tooltip="x"))
        + geom_point()
    )
    plot = interactive(gg=gg)

    html = plot + to_html()
    minified_html = plot + to_html(minify=True)

    assert re.search(r"</style>\s+</head>", html)
    assert "</style></head>" in minified_html
    assert len(minified_html) < len(html)


def test_save_can_minify_output(tmp_path):
    gg = (
        ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", tooltip="x"))
        + geom_point()
    )
    html_path = tmp_path / "chart.html"

    interactive(gg=gg) + save(html_path, minify=True)

    html = html_path.read_text(encoding="utf-8")
    assert "</style></head>" in html


def test_minify_keeps_user_javascript_verbatim():
    # Regression: the previous minifier joined script lines with spaces
    # and dropped `//`-prefixed lines, which commented out code after a
    # trailing comment, broke semicolon-free code, and mutated template
    # literals.
    user_js = (
        'console.log("first"); // mark\n'
        'console.log("second");\n'
        "a = 1\n"
        "b = 2\n"
        "const s = `\n// string content, not a comment\n`;"
    )
    gg = ggplot(data=anscombe_quartet.head(1), mapping=aes(x="x", y="y")) + geom_point()

    html = interactive(gg=gg) + javascript(user_js) + to_html(minify=True)

    assert user_js in html


def test_show_saves_temp_html_and_opens_browser(tmp_path, monkeypatch):
    gg = ggplot(data=anscombe_quartet.head(1), mapping=aes(x="x", y="y")) + geom_point()
    html_path = tmp_path / "show.html"
    opened_urls = []

    def fake_mkstemp(suffix: str):
        assert suffix == ".html"
        fd = os.open(html_path, os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        return fd, str(html_path)

    monkeypatch.setattr(main_module.tempfile, "mkstemp", fake_mkstemp)
    monkeypatch.setattr(
        main_module.webbrowser,
        "open",
        lambda url: opened_urls.append(url) or True,
    )

    result = interactive(gg=gg) + show()

    assert result is None
    assert opened_urls == [f"file://{html_path}"]
    assert "plot-container" in html_path.read_text(encoding="utf-8")


def test_to_iframe_exports_html_in_srcdoc():
    gg = (
        ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", tooltip="x"))
        + geom_point()
    )

    iframe = interactive(gg=gg) + to_iframe(height=480)

    assert iframe.startswith("<iframe ")
    assert 'srcdoc="&lt;!doctype html&gt;' in iframe
    assert 'title="ninejs interactive plot"' in iframe
    assert 'style="width:100%;height:480px;border:0;"' in iframe
    assert 'sandbox="allow-scripts"' in iframe


def test_to_iframe_escapes_attributes_and_allows_omitting_sandbox():
    iframe = to_iframe(
        width=800,
        height="75vh",
        title='A "quoted" plot',
        sandbox=None,
    ).render("<p>x</p>")

    assert 'srcdoc="&lt;p&gt;x&lt;/p&gt;"' in iframe
    assert 'title="A &quot;quoted&quot; plot"' in iframe
    assert 'style="width:800px;height:75vh;border:0;"' in iframe
    assert "sandbox=" not in iframe


def test_interactive_repr_html_exports_default_iframe():
    gg = (
        ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", tooltip="x"))
        + geom_point()
    )

    iframe = interactive(gg=gg)._repr_html_()

    assert iframe.startswith("<iframe ")
    assert iframe.endswith("></iframe>")
    assert 'srcdoc="&lt;!doctype html&gt;' in iframe
    assert 'title="ninejs interactive plot"' in iframe
    assert 'style="width:90%;height:500px;border:0;"' in iframe
    assert 'sandbox="allow-scripts"' in iframe


def test_interactive_repr_html_includes_chained_css():
    gg = (
        ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", tooltip="x"))
        + geom_point()
    )
    plot = interactive(gg=gg) + css(".tooltip { font-weight: bold; }")

    iframe = plot._repr_html_()
    srcdoc = re.search(r'srcdoc="(.*?)"', iframe, re.S)

    assert srcdoc is not None
    assert ".tooltip{font-weight:bold;}" in unescape(srcdoc.group(1))


def test_html_includes_parse_diagnostics():
    gg = (
        ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", tooltip="x"))
        + geom_point()
    )

    html = interactive(gg=gg) + to_html()

    # Local names are mangled by minification; method names and string
    # literals survive.
    assert ".getSvgSummary(" in html
    assert ".getAxesSummary(" in html
    assert ".logParseSummary(" in html
    assert "[ninejs] parsed chart" in html
    assert "<script src=" not in html
    assert "https://cdn" not in html
    assert "sourceMappingURL" not in html
    assert "DOMPurify 3.4.5" in html
    assert "https://d3js.org v7.9.0" in html
