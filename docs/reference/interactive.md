::: ninejs.main.interactive
    options:
      show_root_heading: true

## Save to an HTML file

::: ninejs.main.save
    options:
      show_root_heading: true

## Export to HTML string

::: ninejs.main.to_html
    options:
      show_root_heading: true

## Export to an iframe HTML string

::: ninejs.main.to_iframe
    options:
      show_root_heading: true

## Show preview in editor

!!! tip

    You might not need the `show()` function. In most environments, `ninejs` detects that it needs to display the chart. See [Jupyter display](#jupyter-display).

::: ninejs.main.show
    options:
      show_root_heading: true

## Jupyter display

In JupyterLab, VS Code notebooks or Positron, an `interactive` object renders automatically when it is the last expression in a cell. Internally, the object exposes `_repr_html_()` and returns the same iframe-style HTML as `to_iframe()`.
