---
title: Shiny
---

In [Shiny](https://shiny.posit.co/py/) for Python, use `to_iframe()` to return an iframe-ready HTML string. Inside your `server()` function in `app.py`, you could do something like this:

```python
@reactive.calc
def plot():
   dataset = input.dataset()

   gg = (
      ggplot(
            filtered_data(),
            aes(x="x", y="y", color="dataset", tooltip="tooltip", data_id="dataset"),
      )
      + geom_point(size=input.point_size(), alpha=input.opacity())
      + labs(x="x", y="y", color="Dataset")
      + theme_minimal()
   )

   return gg

@render.ui
def scatter_plot():
   return ui.HTML(
      interactive(plot())
      + to_iframe(
            height="90%",
            width="70%",
            title="Interactive Anscombe scatter plot",
      )
   )
```

![Shiny for Python app rendering a ninejs scatterplot with controls for dataset, point size, and opacity](../img/shiny.png)
