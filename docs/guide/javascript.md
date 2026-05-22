---
title: JavaScript
---

With `ninejs`, you can add your own JavaScript for advanced plot customization. Here's how it works.

## What is JavaScript?

TODO

## Examples

TODO

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
- `svg`: the entire SVG element (e.g., the whole chart)

???+ question

    Something missing? Please [open an issue](https://github.com/y-sunflower/ninejs/issues)!

## Appendix

[^1]: The DOM (Document Object Model) is like a tree structure representing your webpage. JavaScript and CSS use it to select, modify, and interact with elements dynamically.
