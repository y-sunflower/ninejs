# `ninejs`

## Add tooltip

```py
from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import interactive, css, to_html

gg = (
    ggplot(
        data=anscombe_quartet,
        mapping=aes(x="x", y="y", tooltip="dataset"),
    )
    + geom_point(size=7, alpha=0.5)
    + theme_minimal()
)

(
    interactive(gg=gg)
    + css(".tooltip{font-size: 2em;}")
    + to_html(file_path="docs/iframes/point.html")
)
```

<iframe width="800" height="600" src="iframes/point.html" style="border:none;"></iframe>

## Tooltip grouping

```py
from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import interactive, css, to_html

gg = (
    ggplot(
        data=anscombe_quartet,
        mapping=aes(
            x="x",
            y="y",
            color="dataset",
            tooltip="dataset",
            data_id="dataset",
        ),
    )
    + geom_point(size=7, alpha=0.5)
    + theme_minimal()
)

(
    interactive(gg=gg)
    + css(from_dict={".tooltip": {"font-size": "3em"}})
    + to_html(file_path="docs/iframes/quickstart2.html")
)
```

<iframe width="800" height="600" src="iframes/quickstart2.html" style="border:none;"></iframe>

## Line chart

```python
gg = (
    ggplot(
        data=anscombe_quartet,
        mapping=aes(
            x="x",
            y="y",
            color="dataset",
            tooltip="dataset",
        ),
    )
    + geom_line(size=4, alpha=0.5)
    + theme_minimal()
)

(
    interactive(gg=gg)
    + css(from_dict={".tooltip": {"font-size": "3em"}})
    + to_html("docs/iframes/line.html")
)
```

<iframe width="800" height="600" src="iframes/line.html" style="border:none;"></iframe>

## Barplot

```python
df = pd.DataFrame({"category": ["A", "B", "C"], "value": [3, 7, 5]})
df["tooltip"] = df["category"].astype(str) + " (" + df["value"].astype(str) + ")"


gg = (
    ggplot(df, aes(x="category", y="value", tooltip="tooltip"))
    + geom_col()
    + theme_classic()
)

(
    interactive(gg=gg)
    + to_html("docs/iframes/bar.html")
)
```

<iframe width="800" height="600" src="iframes/bar.html" style="border:none;"></iframe>
