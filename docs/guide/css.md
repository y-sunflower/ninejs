---
title: CSS
---

With `ninejs`, you can add your own CSS for advanced plot customization. Here's how it works.

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
from ninejs import interactive, css, save

(
    interactive(gg)
    + css(".tooltip {font-size: 2em;}")
)
```

## Using a Python dictionary

For better readability and reusability, you can define CSS as a dictionary:

```python
(
    interactive(gg)
    + css(from_dict={".tooltip": {"color": "blue", "background": "red"}})
)
```

Method chaining also works if you want to split styles:

```python
(
    interactive(gg)
    + css(".tooltip {font-size: 2em;}")
    + css(from_dict={".tooltip": {"color": "blue", "background": "red"}})
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
(
    interactive(gg)
    + css(from_file="style.css")
)
```

## Selectable elements

To style or add interactivity, you need to select elements using the DOM[^1]. These are the most common selectors:

### Plot elements

- `.point`: scatter plot points
- `.line`: line chart lines
- `.area`: area chart fills
- `.bar`: bar chart bars
- `.polygon`: polygon chart maps
- `.plot-element`: all of the above

You can combine with `.hovered` or `.not-hovered`, e.g., `.point.hovered`.

### Misc

- `.tooltip`: tooltip shown on hover
- `svg`: the entire SVG element (e.g., the whole chart)

???+ question

    Something missing? Please [open an issue](https://github.com/y-sunflower/ninejs/issues)!

## Default CSS

You can find the default CSS applied by ninejs [here](https://github.com/y-sunflower/ninejs/blob/main/ninejs/static/default.css).

## Appendix

[^1]: The DOM (Document Object Model) is like a tree structure representing your webpage. JavaScript and CSS use it to select, modify, and interact with elements dynamically.
