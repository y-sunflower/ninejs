---
title: Matplotlib
---

Use `gg.draw()` when you want direct access to Matplotlib's `fig` and `ax`.
You can add annotations there before exporting the plot with `ninejs`.

```python
from plotnine import aes, geom_point, ggplot, labs, theme_minimal
from plotnine.data import anscombe_quartet
from ninejs import interactive, save

gg = (
    ggplot(
        anscombe_quartet,
        aes(x="x", y="y", color="dataset", tooltip="dataset"),
    )
    + geom_point(size=5, alpha=0.7)
    + labs(x="x", y="y")
    + theme_minimal()
)

fig = gg.draw()
ax = fig.axes[0]

ax.annotate(
    "Added with Matplotlib",
    xy=(16, 8),
    xytext=(12, 11),
    arrowprops={"arrowstyle": "->", "color": "#222222"},
    color="#222222",
)

interactive(gg) + save("docs/iframes/matplotlib.html", minify=True)
```

<iframe width="100%" height="600" src="../iframes/matplotlib.html" style="border:none;"></iframe>

The final line uses `gg`, not `fig`, because `ninejs` reads mappings such as
`tooltip`, `data_id`, and `on_click` from the plotnine object.
