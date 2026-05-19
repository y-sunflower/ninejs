---
title: Positron
---

You can leverage Positron's plot panel via `show()`. It will automatically detect that you're working with an HTML-based plot and open the built-in viewer, which will let you play with your interactive chart:

```python
from plotnine import ggplot, aes, geom_point
from plotnine.data import anscombe_quartet
from ninejs import interactive, show

gg = (
   ggplot(
      data=anscombe_quartet,
      mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
   )
   + geom_point(size=4, alpha=0.7)
)

interactive(gg) + show()
```

![](../img/positron.png)
