# `ninejs`

## Add tooltip

```py
from plotnine import ggplot, aes, geom_point
from plotnine.data import anscombe_quartet
from ninejs import MagicPlot

ggplot(anscombe_quartet, aes(x="x", y="y")) + geom_point(size=7, alpha=0.5)

tooltip = [f"x={val}" for val in anscombe_quartet["x"].to_list()]
MagicPlot().add_tooltip(labels=tooltip).save("quickstart.html")
```

<iframe width="800" height="600" src="iframes/quickstart.html" style="border:none;"/>

## Tooltip grouping

```py
from plotnine import ggplot, aes, geom_point
from plotnine.data import anscombe_quartet

(
   ggplot(anscombe_quartet, aes(x="x", y="y", color="dataset"))
   + geom_point(size=7, alpha=0.5)
)

tooltip = [f"x={val}" for val in anscombe_quartet["x"].to_list()]
MagicPlot().add_tooltip(
   labels=tooltip,
   groups=anscombe_quartet["dataset"],
).save("quickstart.html")
```

<iframe width="800" height="600" src="iframes/quickstart2.html" style="border:none;">
