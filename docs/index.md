# `ninejs`

```py
from plotnine import ggplot, aes, geom_point
from plotnine.data import anscombe_quartet
from ninejs import MagicPlot

ggplot(anscombe_quartet, aes(x="x", y="y")) + geom_point(size=7, alpha=0.5)

tooltip = [f"x={val}" for val in anscombe_quartet["x"].to_list()]
MagicPlot().add_tooltip(labels=tooltip).save("index.html")
```

<iframe width="800" height="600" src="iframes/index.html" style="border:none;">
