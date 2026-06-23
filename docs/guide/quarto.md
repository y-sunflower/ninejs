---
title: Quarto
---

In [Quarto](https://quarto.org/), `ninejs` automatically displays the chart:

````md
---
title: ninejs in a Quarto document
---

```{python}
from plotnine import ggplot, aes, geom_point
from plotnine.data import anscombe_quartet
from ninejs import interactive

gg = (
   ggplot(
      data=anscombe_quartet,
      mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
   )
   + geom_point(size=4, alpha=0.7)
)

interactive(gg)
```
````

![Quarto document rendering ninejs code above an Anscombe quartet scatterplot](../img/quarto.png)
