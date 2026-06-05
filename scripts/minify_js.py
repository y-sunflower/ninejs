"""
Bundle and minify the browser parser modules into
`ninejs/static/PlotParser.min.js`.

The output keeps top-level names (terser's default): the template
references `PlotSVGParser` from code appended after the bundle, so
top-level declarations must survive minification untouched.

The first line records a hash of the source modules so tests can detect
a stale bundle without needing terser.

Run with: just minify-js
"""

import hashlib
import subprocess

from ninejs.main import JS_PARSER_MODULE_PATHS, TEMPLATE_DIR
from ninejs.utils import _get_js_module_bundle

OUTPUT_PATH = TEMPLATE_DIR / "PlotParser.min.js"


def main() -> None:
    bundle = _get_js_module_bundle(JS_PARSER_MODULE_PATHS)
    sources_hash = hashlib.sha256(bundle.encode()).hexdigest()

    minified = subprocess.run(
        ["bunx", "terser", "--compress", "--mangle"],
        input=bundle,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    OUTPUT_PATH.write_text(f"// ninejs-sources-hash: {sources_hash}\n{minified}\n")
    print(f"Wrote {OUTPUT_PATH} ({len(minified):,} bytes from {len(bundle):,})")


if __name__ == "__main__":
    main()
