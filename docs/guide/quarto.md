---
title: Quarto
---

The simplest way to embed your plot in [Quarto](https://quarto.org/) is to save it as an HTML file, and then add an <iframe\> below.

````md
---
title: ninejs in a Quarto document
---

```{python}
from plotnine import ggplot, aes, geom_point
from plotnine.data import anscombe_quartet
from ninejs import interactive, save

gg = (
   ggplot(
      data=anscombe_quartet,
      mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
   )
   + geom_point(size=4, alpha=0.7)
)

interactive(gg) + save("plot.html")
```

<iframe width="800" height="600" src="plot.html" style="border:none;"></iframe>
````

![Quarto document rendering ninejs code above an Anscombe quartet scatterplot](../img/quarto.png)
