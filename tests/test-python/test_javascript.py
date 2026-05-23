from ninejs.javascript import js_from_file, javascript
import ninejs
from ninejs import effects
from plotnine import ggplot, aes, geom_point, theme_minimal

from ninejs.data import anscombe_quartet


def test_from_file_reads_js(tmp_path):
    js_file = tmp_path / "style.js"
    js_file.write_text("console.log('testing javascript')")
    assert js_from_file(str(js_file)) == "console.log('testing javascript')"


def test_confetti_effect_loads_bundle_once_and_runs_each_call():
    assert 'if (typeof globalThis.confetti !== "function")' in effects.confetti
    assert "globalThis.confetti({" in effects.confetti


def test_adding_js_actually_adds_js():
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
        )
        + geom_point(size=4, alpha=0.7)
        + theme_minimal()
    )

    ip = ninejs.interactive(gg) + javascript("console.log('testing adding javascript')")
    assert ip.plot.additional_javascript == "console.log('testing adding javascript')"
