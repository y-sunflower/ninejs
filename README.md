<img src="https://github.com/JosephBARBIERDARNAL/static/blob/main/python-libs/ninejs/image.png?raw=true" alt="ninejs logo" align="right" width="150px"/>

<div style="font-size: 1.6em">

# ninejs

</div>

Bringing ✨***interactivity***✨ to [plotnine](https://plotnine.org/).

`ninejs` lets you add tooltips and hover grouping to plotnine plots directly from `aes()` via the `tooltip` and `data_id` aesthetic mappings, then export the result as a standalone HTML plot **with just 2 or 3 lines of code**.

It works out of the box with Jupyter, Quarto, marimo, Streamlit, and Shiny, and it includes a built-in preview in Positron.

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
      aes(x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset")
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
