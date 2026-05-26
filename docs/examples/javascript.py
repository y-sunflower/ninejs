import pandas as pd
from plotnine import aes, geom_col, ggplot, labs, theme_minimal

from ninejs import interactive, save, javascript

df = pd.DataFrame({"category": ["A", "B", "C", "D", "E"], "value": [3, 7, 5, 9, 4]})

gg = (
    ggplot(df, aes(x="category", y="value", tooltip="category"))
    + geom_col(fill="#4C78A8")
    + labs(x="Category", y="Value")
    + theme_minimal()
)


hello_js = """
document.querySelectorAll(".bar").forEach((bar) => {
  bar.addEventListener("click", () => alert("You clicked a bar!"));
});
"""

(
    interactive(gg)
    + javascript(hello_js)
    + save("docs/iframes/javascript-hello.html", minify=True)
)


click_color_js = """
document.querySelectorAll(".bar").forEach((bar) => {
  bar.addEventListener("click", () => {
    bar.setAttribute("fill", "#E63946");
  });
});
"""

(
    interactive(gg)
    + javascript(click_color_js)
    + save("docs/iframes/javascript-click-color.html", minify=True)
)


animate_js = """
document.querySelectorAll(".bar").forEach((bar, i) => {
  bar.style.opacity = "0";
  bar.style.transition = "opacity 0.6s ease";
  setTimeout(() => { bar.style.opacity = "1"; }, i * 200);
});
"""

(
    interactive(gg)
    + javascript(animate_js)
    + save("docs/iframes/javascript-animate.html", minify=True)
)
