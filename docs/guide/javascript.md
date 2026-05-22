---
title: JavaScript
---

With `ninejs`, you can add your own JavaScript for advanced plot customization. Here's how it works.

## What is JavaScript?

JavaScript is the language that makes web pages interactive: it reacts to clicks, animates elements, and changes the page on the fly. It runs directly in the browser, on the page where your plot is displayed.

A tiny JavaScript snippet looks like this:

```js
document.querySelectorAll(".bar").forEach((bar) => {
  bar.addEventListener("click", () => alert("You clicked a bar!"));
});
```

This means: _"For every element with class `bar`, when it's clicked, show an alert."_

## Applying JavaScript to a plot

You can directly apply a JavaScript string to your plot:

```python
import pandas as pd
from plotnine import aes, geom_col, ggplot, labs, theme_minimal

from ninejs import interactive, save, javascript

df = pd.DataFrame({"category": ["A", "B", "C", "D", "E"], "value": [3, 7, 5, 9, 4]})

gg = (
    ggplot(df, aes(x="category", y="value", tooltip="category"))
    + geom_col(fill="#4C78A8")
    + labs(x="Category", y="Value")
    + theme_minimal()
)

hello_js = """
document.querySelectorAll(".bar").forEach((bar) => {
  bar.addEventListener("click", () => alert("You clicked a bar!"));
});
"""

(
    interactive(gg)
    + javascript(hello_js)
    + save("docs/iframes/javascript-hello.html")
)
```

<iframe width="100%" height="500" src="../iframes/javascript-hello.html" style="border:none;"></iframe>

!!! warning

    JavaScript you add this way runs as-is in the generated page. Only use code you trust.

## Examples

=== "Change color on click"

    Mutate the bar's `fill` attribute when clicked.

    ```py
    js = """
    document.querySelectorAll(".bar").forEach((bar) => {
    bar.addEventListener("click", () => {
        bar.setAttribute("style", "fill: #E63946");
    });
    });
    """

    interactive(gg) + javascript(js) + save("docs/iframes/javascript-click-color.html")
    ```

    <iframe width="100%" height="500" src="../iframes/javascript-click-color.html" style="border:none;"></iframe>

=== "Animate on load"

    Fade the bars in one after the other when the chart loads (refresh the page to show the animation).

    ```py
    js = """
    document.querySelectorAll(".bar").forEach((bar, i) => {
    bar.style.opacity = "0";
    bar.style.transition = "opacity 0.6s ease";
    setTimeout(() => { bar.style.opacity = "1"; }, i * 200);
    });
    """

    interactive(gg) + javascript(js) + save("docs/iframes/javascript-animate.html")
    ```

    <iframe width="100%" height="500" src="../iframes/javascript-animate.html" style="border:none;"></iframe>

## Selectable elements

To style or add interactivity, you need to select elements using the DOM[^1]. These are the most common selectors:

### Plot elements

- `.point`: scatter plot points
- `.line`: line chart lines
- `.area`: area chart fills
- `.bar`: bar chart bars
- `.polygons`: polygon chart maps
- `.plot-element`: all of the above

You can combine with `.hovered` or `.not-hovered`, e.g., `.point.hovered`.

### Misc

- `.tooltip`: tooltip shown on hover
- `svg`: the entire SVG element (e.g., the whole chart)

???+ question

    Something missing? Please [open an issue](https://github.com/y-sunflower/ninejs/issues)!

## Appendix

[^1]: The DOM (Document Object Model) is like a tree structure representing your webpage. JavaScript and CSS use it to select, modify, and interact with elements dynamically.
