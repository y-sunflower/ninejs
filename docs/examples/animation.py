import pandas as pd
from plotnine import aes, geom_col, ggplot, labs, theme_minimal, theme

from ninejs import interactive, save, javascript

df = pd.DataFrame({"category": ["A", "B", "C", "D", "E"], "value": [3, 7, 5, 9, 4]})

gg = (
    ggplot(df, aes(x="category", y="value"))
    + geom_col(fill="#fb8500", width=0.6, color="black", size=1)
    + labs(x="Category", y="Value")
    + theme_minimal()
    + theme(figure_size=(8, 5))
)

js = """
document.querySelectorAll(".bar").forEach((bar, i) => {
    bar.style.transformBox = "fill-box";
    bar.style.transformOrigin = "bottom";
    bar.style.transform = "scaleY(0)";
    bar.style.transition = "transform 0.7s cubic-bezier(.2,.8,.2,1)";

    setTimeout(() => {
        bar.style.transform = "scaleY(1)";
    }, i * 80);
});
"""

interactive(gg) + javascript(js) + save("docs/iframes/animation.html", minify=True)
