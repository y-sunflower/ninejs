# `ninejs`

## Add tooltip

```py
from plotnine import ggplot, aes, geom_point
from plotnine.data import anscombe_quartet

from ninejs import make_interactive

gg = ggplot(
    anscombe_quartet,
    aes(x="x", y="y", color="dataset", tooltip="dataset"),
) + geom_point(size=7, alpha=0.5)

make_interactive(gg, "docs/iframes/quickstart.html")
```

<iframe width="800" height="600" src="iframes/quickstart.html" style="border:none;"></iframe>

## Tooltip grouping

```py
from plotnine import ggplot, aes, geom_point
from plotnine.data import anscombe_quartet

from ninejs import make_interactive

gg = ggplot(
    anscombe_quartet,
    aes(x="x", y="y", color="dataset", tooltip="dataset", data_id="dataset"),
) + geom_point(size=7, alpha=0.5)

make_interactive(gg, "docs/iframes/quickstart2.html")
```

<iframe width="800" height="600" src="iframes/quickstart2.html" style="border:none;"></iframe>
