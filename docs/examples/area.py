from plotnine import (
    ggplot,
    aes,
    geom_area,
    theme_minimal,
    labs,
    scale_x_date,
    theme,
    element_text,
)
from ninejs import interactive, save
import pandas as pd

# Sample data
df = pd.DataFrame(
    {
        "date": pd.date_range("2025-01-01", periods=12, freq="ME").tolist() * 3,
        "value": (
            [12, 18, 15, 22, 30, 28, 35, 40, 38, 45, 50, 48]
            + [8, 12, 10, 15, 18, 20, 24, 26, 25, 28, 30, 32]
            + [5, 7, 9, 11, 14, 13, 16, 18, 20, 19, 22, 24]
        ),
        "group": (["Product A"] * 12 + ["Product B"] * 12 + ["Product C"] * 12),
    }
)

# Stacked area chart
gg = (
    ggplot(df, aes(x="date", y="value", fill="group", tooltip="group"))
    + geom_area(alpha=0.8)
    + theme_minimal()
    + labs(title="Monthly Growth by Product", x="Date", y="Value", fill="Category")
    + scale_x_date(date_labels="%b")
    + theme(
        figure_size=(10, 5),
        plot_title=element_text(size=16, weight="bold"),
        axis_title=element_text(size=11),
        axis_text=element_text(size=10),
        legend_title=element_text(size=11),
        legend_text=element_text(size=10),
    )
)

interactive(gg) + save("docs/iframes/area-chart.html")
