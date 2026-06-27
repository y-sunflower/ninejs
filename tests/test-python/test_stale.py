import hashlib
from ninejs.utils import _get_js_module_bundle
import ninejs.main as main_module


def test_plot_parser_min_bundle_is_up_to_date():
    """
    ninejs requires javascript to be minified, and it tests
    check whether the current minified version is up to date.
    """
    bundle = _get_js_module_bundle(main_module.JS_PARSER_MODULE_PATHS)
    sources_hash = hashlib.sha256(bundle.encode()).hexdigest()

    first_line = main_module.JS_PARSER_MIN_PATH.read_text(
        encoding="utf-8"
    ).splitlines()[0]

    assert first_line == f"// ninejs-sources-hash: {sources_hash}", (
        "PlotParser.min.js is stale; run `just minify-js` or `script/minify_js.py`"
    )
