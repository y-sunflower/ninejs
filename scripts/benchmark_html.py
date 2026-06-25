from __future__ import annotations

import argparse
import gzip
import json
import re
from pathlib import Path
from typing import Any


def _script_text(html: str, script_id: str) -> str:
    match = re.search(
        rf'<script id="{re.escape(script_id)}"[^>]*>\s*(.*?)\s*</script>',
        html,
        re.S,
    )
    return match.group(1) if match else ""


def _measure_file(path: Path) -> dict[str, Any]:
    html_bytes = path.read_bytes()
    html = html_bytes.decode("utf-8", errors="replace")
    plot_data = _script_text(html, "plot-data")

    return {
        "file": str(path),
        "bytes": len(html_bytes),
        "gzip_bytes": len(gzip.compress(html_bytes, compresslevel=9)),
        "path_tags": html.count("<path "),
        "clip_paths": html.count("<clipPath"),
        "plot_data_bytes": len(plot_data.encode()),
        "plot_element_mentions": html.count("plot-element"),
    }


def _measure_browser(path: Path, hover_selector: str | None) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    try:
        page.goto(f"file://{path.resolve()}", wait_until="load")
        page.wait_for_selector("svg", timeout=5000)
        page.wait_for_selector(".tooltip", state="attached", timeout=5000)
        page.wait_for_timeout(100)
        metrics = page.evaluate(
            """() => {
              const nav = performance.getEntriesByType("navigation")[0];
              return {
                dom_content_loaded_ms: nav.domContentLoadedEventEnd - nav.startTime,
                load_ms: nav.loadEventEnd - nav.startTime,
                dom_paths: document.querySelectorAll("path").length,
                interactive_elements: document.querySelectorAll(".plot-element").length
              };
            }"""
        )

        if hover_selector:
            hover_timing = page.evaluate(
                """(selector) => {
                  const node = document.querySelector(selector);
                  if (!node) return null;
                  const rect = node.getBoundingClientRect();
                  const x = rect.left + rect.width / 2;
                  const y = rect.top + rect.height / 2;
                  const start = performance.now();
                  node.dispatchEvent(new MouseEvent("mouseover", {
                    bubbles: true,
                    pageX: x,
                    pageY: y,
                    clientX: x,
                    clientY: y,
                    view: window
                  }));
                  return performance.now() - start;
                }""",
                hover_selector,
            )
            metrics["hover_ms"] = hover_timing

        return metrics
    finally:
        browser.close()
        playwright.stop()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Measure exported ninejs HTML payload and browser timing."
    )
    parser.add_argument("html", nargs="+", type=Path)
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Launch Chromium with Playwright and collect load/DOM metrics.",
    )
    parser.add_argument(
        "--hover-selector",
        help="Optional CSS selector to dispatch one mouseover timing sample.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON lines.")
    args = parser.parse_args()

    rows = []
    for path in args.html:
        row = _measure_file(path)
        if args.browser:
            row.update(_measure_browser(path, args.hover_selector))
        rows.append(row)

    if args.json:
        for row in rows:
            print(json.dumps(row, sort_keys=True))
        return

    headers = sorted({key for row in rows for key in row})
    print("\t".join(headers))
    for row in rows:
        print("\t".join(str(row.get(header, "")) for header in headers))


if __name__ == "__main__":
    main()
