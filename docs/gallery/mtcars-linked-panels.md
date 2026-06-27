---
title: Linked mtcars panels
---

This example uses plotnine's native composition operators to link a scatter plot
and a bar chart. Hovering a car in either panel highlights the matching car in
the other panel.

```py
import plotnine as gg
from plotnine.data import mtcars

from ninejs import css, interactive, save


mtcars = mtcars.rename(columns={"name": "carname"}).copy()
mtcars["car_id"] = mtcars["carname"].str.replace(r"\W+", "-", regex=True)
mtcars["tooltip"] = [
    f"{carname}<br>MPG: {mpg}<br>Displacement: {disp}<br>Quarter mile: {qsec}s"
    for carname, mpg, disp, qsec in zip(
        mtcars["carname"],
        mtcars["mpg"],
        mtcars["disp"],
        mtcars["qsec"],
        strict=True,
    )
]

mapping = gg.aes(tooltip="tooltip", data_id="car_id", hover_key="car_id")

scatter_plot = (
    gg.ggplot(mtcars, gg.aes("disp", "qsec"))
    + gg.geom_point(mapping=mapping, size=3, fill="#333333", color="#333333")
    + gg.labs(
        title="Displacement vs quarter-mile time",
        x="Displacement",
        y="Quarter mile (seconds)",
    )
    + gg.theme_minimal(base_size=10)
)

bar_plot = (
    gg.ggplot(mtcars, gg.aes("reorder(carname, mpg)", "mpg"))
    + gg.geom_col(mapping=mapping, fill="skyblue", color="white", size=0.35)
    + gg.coord_flip()
    + gg.labs(title="Miles per gallon by car", x="", y="Miles per gallon")
    + gg.theme_minimal(base_size=10)
)

plot = (scatter_plot | bar_plot) & gg.theme(
    figure_size=(11, 7),
    plot_background=gg.element_rect(fill="white", color="white"),
    panel_background=gg.element_rect(fill="white", color="white"),
    plot_title=gg.element_text(size=12, weight="bold"),
)

(
    interactive(plot, hover_nearest=True)
    + css(from_dict={".plot-element.hovered": {"fill": "red", "stroke": "black"}})
    + save("docs/iframes/mtcars-linked-panels.html", minify=True)
)
```

<iframe width="100%" height="720" src="../iframes/mtcars-linked-panels.html" style="border:none;"></iframe>
