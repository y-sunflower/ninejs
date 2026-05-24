---
title: On click
---

`ninejs` lets you also add effects when clicking plot elements via the `on_click` aesthetic mapping. This expects some JavaScript code that will be executed when clicking on something.

For example, here we add a `click_url` columns to our dataframe. The column contains some JavaScript that opens a new tab in the browser and go to the specified url. **Try to click on a point!**

```py hl_lines="6"
from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet

from ninejs import interactive, save

anscombe_quartet["open_url"] = "window.open('https://www.ysunflower.com/')"

gg = (
    ggplot(
        data=anscombe_quartet,
        mapping=aes(
            x="x",
            y="y",
            color="dataset",
            tooltip="dataset",
            on_click="open_url",
        ),
    )
    + geom_point(size=7, alpha=0.7)
    + theme_minimal()
)

interactive(gg) + save("docs/iframes/on-click-new-window.html")
```

<iframe width="100%" height="600" src="../iframes/on-click-new-window.html" style="border:none;"></iframe>

But since the `on_click` aesthetic uses a column from the data, the effect can be dependent on your data!

```py hl_lines="6"
from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet as df

from ninejs import interactive, save

df["alert"] = "alert('You clicked on: " + df["dataset"] + "');"

gg = (
    ggplot(
        data=df,
        mapping=aes(x="x", y="y", color="dataset", tooltip="dataset", on_click="alert"),
    )
    + geom_point(size=7, alpha=0.7)
    + theme_minimal()
)

interactive(gg) + save("docs/iframes/on-click-custom-alert.html")
```

<iframe width="100%" height="600" src="../iframes/on-click-custom-alert.html" style="border:none;"></iframe>

## Understanding `event.target`

You can use `event.target` inside your `on_click` aesthetic to select the **clicked element**. For example, here we toggle the class `selected` on the clicked element, adding it if the element doesn't have it, or removing it if it does.

Then we add some CSS to say that elements of the class `selected` have a light black stroke.

```py hl_lines="6 25"
from plotnine import ggplot, aes, geom_point, theme_minimal
from plotnine.data import anscombe_quartet as df

from ninejs import interactive, save, css

df["stroke"] = "event.target.classList.toggle('selected')"

gg = (
    ggplot(
        data=df,
        mapping=aes(
            x="x",
            y="y",
            color="dataset",
            tooltip="dataset",
            on_click="stroke",
        ),
    )
    + geom_point(size=7, alpha=0.7)
    + theme_minimal()
)

(
    interactive(gg)
    + css(from_dict={".selected": {"stroke": "black", "stroke-width": "1px"}})
    + save("docs/iframes/on-click-stroke.html")
)
```

<iframe width="100%" height="600" src="../iframes/on-click-stroke.html" style="border:none;"></iframe>

!!! tip

    This is a very basic usage, but you could do much more advanced things (e.g., tracking how people interact with your chart by sending a request to a server on every click).
