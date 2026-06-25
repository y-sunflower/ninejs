<img src="https://github.com/JosephBARBIERDARNAL/static/blob/main/python-libs/ninejs/image.png?raw=true" alt="ninejs logo" align="right" width="150px"/>

<div style="font-size: 1.6em">

# ninejs

![Coverage](./coverage-badge.svg)
![Python Versions](https://img.shields.io/badge/Python-3.10–3.14-blue)

</div>

Bringing ✨***interactivity***✨ to [plotnine](https://plotnine.org/).

`ninejs` adds interactive behavior to plotnine charts with a minimal API. You can attach tooltips, hover grouping, and on click events directly from `aes()`, then export the result as a standalone HTML plot. All of this **with just 2 or 3 lines of code**!

- Works out of the box with [Jupyter](https://y-sunflower.github.io/ninejs/guide/jupyter), [Quarto](https://y-sunflower.github.io/ninejs/guide/quarto), [Marimo](https://y-sunflower.github.io/ninejs/guide/marimo), and [Shiny](https://y-sunflower.github.io/ninejs/guide/shiny)
- Includes a built-in [preview in Positron](https://y-sunflower.github.io/ninejs/guide/positron)
- Supports custom [CSS](https://y-sunflower.github.io/ninejs/guide/css) and [JS](https://y-sunflower.github.io/ninejs/guide/javascript)
- Copy-pastable [self contained documentation](https://y-sunflower.github.io/ninejs/#llms-and-agents-llmstxt) for AI and agents

See [examples](https://y-sunflower.github.io/ninejs/).

<br>

## Quick start

```python
from plotnine import aes, geom_point, ggplot, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import css, interactive, save

gg = (
  ggplot(
      anscombe_quartet,
      aes(x="x", y="y", color="dataset", tooltip="dataset", hover_group="dataset")
  )
  + geom_point(size=7, alpha=0.5)
  + theme_minimal()
)

(
  interactive(gg)
  + css(from_dict={".tooltip": {"font-size": "2em"}})
  + save("plot.html")
)
```

![Interactive scatterplot of Anscombe's quartet grouped by dataset with a visible tooltip](./quick-start.png)

<br>

## Installation

```bash
pip install ninejs
```

<br>

## Documentation

See the full documentation and examples [here](https://y-sunflower.github.io/ninejs/).

See [the contributing guide](docs/contributing.md) for local setup, tests, and formatting.
