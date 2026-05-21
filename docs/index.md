<br>

<div align="center" style="font-size: 1.6em">

<h1>ninejs</h1>

<div align="right" style="font-size: 0.8em">

Bringing ✨<b><i>interactivity</i></b>✨ to <a href="https://plotnine.org/">plotnine</a>.

</div>

</div>

`ninejs` adds interactive behavior to plotnine charts with a minimal, composable API. You can attach tooltips, hover grouping, and other frontend interactions directly from `aes()`, then export the result as a standalone HTML plot.

It works out of the box with Quarto, marimo, and Shiny, and it includes a built-in preview in Positron.

## Quick start

Specify the `tooltip` and `data_id` aesthetic mappings, and then pass your plotnine chart to `interactive()`:

```py
from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import interactive, css, save

gg = (
    ggplot(
        data=anscombe_quartet,
        mapping=aes(x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset"),
    )
    + geom_point(size=7, alpha=0.5)
    + theme_minimal()
)

(
    interactive(gg)
    + css(from_dict={".tooltip": {"font-size": "3em"}})
    + save("docs/iframes/quickstart2.html")
)
```

<iframe width="800" height="600" src="iframes/quickstart2.html" style="border:none;"></iframe>

## Installation

=== "pip"

    ```
    pip install ninejs
    ```

=== "uv"

    ```
    uv add ninejs
    ```

=== "pixi"

    ```
    pixi add ninejs
    ```

## Examples

=== "Tooltip"

    ```py
    gg = (
        ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", tooltip="dataset"))
        + geom_point(size=7, alpha=0.5)
        + theme_minimal()
    )

    (
        interactive(gg)
        + css(".tooltip {font-size: 2em;}")
        + save("docs/iframes/point.html")
    )
    ```

    <iframe width="800" height="600" src="iframes/point.html" style="border:none;"></iframe>

=== "Line chart"

    ```python
    gg = (
        ggplot(
            data=anscombe_quartet,
            mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
        )
        + geom_line(size=4, alpha=0.5)
        + theme_minimal()
    )

    (
        interactive(gg)
        + css(from_dict={".tooltip": {"font-size": "3em"}})
        + save("docs/iframes/line.html")
    )
    ```

    <iframe width="800" height="600" src="iframes/line.html" style="border:none;"></iframe>

=== "Bar plot"

    ```python
    gg = (
        ggplot(df, aes(x="category", y="value", tooltip="tooltip"))
        + geom_col()
        + theme_classic()
    )

    interactive(gg) + save("docs/iframes/bar.html")
    ```

    <iframe width="800" height="600" src="iframes/bar.html" style="border:none;"></iframe>

=== "Facet"

    ```python
    gg = (
        ggplot(anscombe_quartet, aes("x", "y", tooltip="x"))
        + geom_point(color="sienna", fill="orange", size=3)
        + geom_smooth(method="lm", se=False, fullrange=True, color="steelblue", size=1)
        + facet_wrap("dataset")
        + labs(title="Anscombe’s Quartet")
        + scale_y_continuous(breaks=(4, 8, 12))
        + coord_fixed(xlim=(3, 22), ylim=(2, 14))
        + theme_tufte(base_family="Futura", base_size=16)
        + theme(
            axis_line=element_line(color="#4d4d4d"),
            axis_ticks_major=element_line(color="#00000000"),
            axis_title=element_blank(),
            panel_spacing=0.09,
        )
    )

    interactive(gg) + save("docs/iframes/facet_wrap.html")
    ```

    <iframe width="800" height="600" src="iframes/facet_wrap.html" style="border:none;"></iframe>

=== "Area chart"

    ```python
    gg = (
        ggplot(df, aes(x="date", y="value", fill="group", tooltip="group"))
        + geom_area(alpha=0.8)
        + theme_minimal()
        + labs(title="Monthly Growth by Product", x="Date", y="Value", fill="Category")
        + scale_x_date(date_labels="%b")
        + theme(
            figure_size=(10, 5),
            plot_title=element_text(size=16, weight="bold"),
            axis_title=element_text(size=11),
            axis_text=element_text(size=10),
            legend_title=element_text(size=11),
            legend_text=element_text(size=10),
        )
    )

    interactive(gg) + save("docs/iframes/area-chart.html")
    ```

    <iframe width="800" height="600" src="iframes/area-chart.html" style="border:none;"></iframe>

## LLMs and agents (llms.txt)

A single-file overview of the ninejs API, written for LLMs and coding agents. This file contains **everything** an agent needs to know to use `ninejs` properly!

<div class="llms-actions">
  <button type="button" id="llms-copy" class="llms-btn">Copy</button>
  <a id="llms-download" class="llms-btn" href="llms.txt" download="llms.txt">Download</a>
  <span id="llms-status" class="llms-status" aria-live="polite"></span>
</div>

<style>
.llms-actions {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.llms-btn {
  display: inline-flex;
  align-items: center;
  padding: 0.4rem 0.9rem;
  font-size: 0.85rem;
  font-weight: 500;
  line-height: 1;
  color: inherit;
  background: transparent;
  border: 1px solid currentColor;
  border-radius: 6px;
  cursor: pointer;
  text-decoration: none;
  opacity: 0.75;
  transition: opacity 0.15s ease, background-color 0.15s ease;
}
.llms-btn:hover,
.llms-btn:focus-visible {
  opacity: 1;
  background-color: rgba(127, 127, 127, 0.08);
  outline: none;
}
.llms-status {
  font-size: 0.8rem;
  opacity: 0.7;
}
</style>

<script>
(function () {
  var copyBtn = document.getElementById("llms-copy");
  var status = document.getElementById("llms-status");
  if (!copyBtn) return;
  copyBtn.addEventListener("click", async function () {
    try {
      var res = await fetch("llms.txt", { cache: "no-store" });
      if (!res.ok) throw new Error("Failed to fetch llms.txt: " + res.status);
      var text = await res.text();
      await navigator.clipboard.writeText(text);
      status.textContent = "Copied";
    } catch (e) {
      status.textContent = "Copy failed";
    }
    setTimeout(function () { status.textContent = ""; }, 2000);
  });
})();
</script>
