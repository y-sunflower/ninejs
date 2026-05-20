---
title: CSS
---

With `plotjs`, you can add your own CSS for advanced plot customization. Here's how it works.

## What is CSS?

CSS has two main components:

- **Selectors**: which elements the style applies to
- **Rules**: a set of `key: value` pairs defining the style

A basic CSS rule looks like this:

```css
.tooltip {
  background: red;
  color: blue;
}
```

This means: _"For all elements with class `tooltip`, set the background to red and the text color to blue."_

## Applying CSS to a plot

You can directly apply a CSS string to your plot:

```python
(
    PlotJS()
    .add_tooltip(labels=df["tooltip"])
    .add_css(".tooltip { background: red; color: blue; }")
)
```

<iframe width="800" height="600" src="../../iframes/CSS.html" style="border:none;"></iframe>

> CSS doesn’t require indentation: one-liners work fine.

## Using a Python dictionary

For better readability and reusability, you can define CSS as a dictionary:

```python
from plotjs import css

(
    PlotJS()
    .add_tooltip(labels=df["tooltip"])
    .add_css(from_dict = {
        ".tooltip": {
            "background": "red",
            "color": "blue"
        }
    })
)
```

Method chaining also works if you want to split styles:

```python
(
    PlotJS()
    .add_tooltip(labels=df["tooltip"])
    .add_css(from_dict = {".tooltip": {"color": "blue"}})
    .add_css(from_dict = {".tooltip": {"background": "red"}})
)
```

## Loading CSS from a file

If your CSS is stored in a `.css` file like:

```css
.tooltip {
  background: pink;
  color: yellow;
}
```

You can load it with:

```python
from plotjs import css

(
    PlotJS()
    .add_tooltip(labels=df["tooltip"])
    .add_css(from_file = "docs/static/style.css")
)
```

<iframe width="800" height="600" src="../../iframes/CSS-2.html" style="border:none;"></iframe>

## Selectable elements

To style or add interactivity, you need to select elements using the DOM[^1]. These are the most common selectors:

### Plot elements

- `.point`: scatter plot points
- `.line`: line chart lines
- `.area`: area chart fills
- `.bar`: bar chart bars
- `.plot-element`: all of the above

You can combine with `.hovered` or `.not-hovered`, e.g., `.point.hovered`.

### Misc

- `.tooltip`: tooltip shown on hover
- `svg`: the entire SVG element

???+ question

    Something missing? Please [open an issue](https://github.com/y-sunflower/plotjs/issues)!

## Default CSS

You can find the default CSS applied by plotjs [here](https://github.com/y-sunflower/plotjs/blob/main/plotjs/static/default.css).

## Appendix

[^1]: The DOM (Document Object Model) is like a tree structure representing your webpage. JavaScript and CSS use it to select, modify, and interact with elements dynamically.
