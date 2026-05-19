<div align="center" style="font-size: 1.6em">

# ninejs

</div>

<div align="right">

Bringing ✨***interactivity***✨ to [plotnine](https://plotnine.org/).

</div>

`ninejs` lets you add tooltips and hover grouping to plotnine plots directly from `aes()` via the `tooltip` and `data_id` aesthetic mappings, then export the result as a standalone HTML plot.

It works out of the box with Quarto, marimo, and Shiny, and it includes a built-in preview in Positron.

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

## Integration

`ninejs` integrates with other tools out of the box.

- Quarto

![Quarto document rendering ninejs code above an Anscombe quartet scatterplot](./docs/img/quarto.png)

- Marimo

![Marimo notebook rendering ninejs code above an Anscombe quartet scatterplot](./docs/img/marimo.png)

- Shiny

![Shiny for Python app rendering a ninejs scatterplot with controls for dataset, point size, and opacity](./docs/img/shiny.png)

- Positron

![Positron viewer showing a ninejs Anscombe quartet scatterplot next to the Python source code](./docs/img/positron.png)

- Anywhere: `ninejs` outputs HTML files that only need a browser, so websites and web-based tools can embed them easily.

The next targets are:

- Jupyter
- Streamlit

<br>

## Documentation

See the full documentation and examples [here](https://y-sunflower.github.io/ninejs/).

See [the contributing guide](docs/contributing.md) for local setup, tests, and formatting.
