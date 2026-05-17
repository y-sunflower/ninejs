# ninejs

Bring interactivity to [plotnine](https://plotnine.org/) charts.

`ninejs` lets you add tooltips and hover grouping to plotnine plots directly from `aes(...)`, then export the result as standalone HTML.

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

![](./quick-start.png)

<br>

## Installation

```bash
pip install ninejs
```

<br>

## Documentation

See the full documentation and examples [here](https://y-sunflower.github.io/ninejs/).
