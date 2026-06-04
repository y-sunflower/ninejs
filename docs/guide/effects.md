`ninejs` bundles a bunch of what is called "effects". An effect is just an interaction, a feature or more generally a specific action that you can trigger whenever you want.

For example, `ninejs` has the **confetti effect** that you can use to add confetti when clicking something for instance.

## Confetti

```python hl_lines="6 12"
from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import interactive, save, effects

anscombe_quartet["confetti"] = effects.confetti()

gg = (
    ggplot(
        data=anscombe_quartet,
        mapping=aes(
            x="x", y="y", color="dataset", tooltip="dataset", on_click="confetti"
        ),
    )
    + geom_point(size=7, alpha=0.7)
    + theme_minimal()
)

interactive(gg) + save("docs/iframes/effects-confetti.html")
```

<iframe width="100%" height="500" src="../iframes/effects-confetti.html" style="border:none;"></iframe>
