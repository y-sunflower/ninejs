---
title: Jupyter
---

In JupyterLab and VS Code notebooks, put the `interactive()` object as the last expression in a cell. The notebook will render it as an interactive iframe:

```python
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

You can still chain CSS or JavaScript before the final expression:

```python
from ninejs import css

interactive(gg) + css(".tooltip { font-size: 1.2rem; }")
```

If you need an explicit HTML string instead, use `to_html()` or `to_iframe()`.
