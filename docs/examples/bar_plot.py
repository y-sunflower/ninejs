import pandas as pd
from plotnine import aes, geom_col, ggplot, theme_classic

from ninejs import interactive, save

df = pd.DataFrame({"category": ["A", "B", "C"], "value": [3, 7, 5]})
df["tooltip"] = [
    f"{category} ({value})"
    for category, value in zip(df["category"], df["value"], strict=True)
]

gg = (
    ggplot(df, aes(x="category", y="value", tooltip="tooltip"))
    + geom_col()
    + theme_classic()
)

interactive(gg) + save("docs/iframes/bar.html")
