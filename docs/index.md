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
    + to_html(file_path="docs/iframes/quickstart.html")
)
```

<iframe width="800" height="600" src="iframes/quickstart.html" style="border:none;"></iframe>

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
