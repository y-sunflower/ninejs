from plotnine import aes, geom_line, ggplot, theme_minimal, theme
from plotnine.data import economics

from ninejs import interactive, javascript, save

gg = (
    ggplot(
        economics.head(120),
        aes(x="date", y="unemploy", tooltip="unemploy"),
    )
    + geom_line(size=2, color="#E45756")
    + theme_minimal()
    + theme(figure_size=(8, 5))
)

js = """
document.querySelectorAll(".line").forEach((line) => {
    const length = line.getTotalLength();

    line.style.strokeDasharray = length;
    line.style.strokeDashoffset = length;
    line.style.transition = "stroke-dashoffset 1s ease";

    line.getBoundingClientRect();

    setTimeout(() => {
        line.style.strokeDashoffset = "0";
    }, 1500);
});
"""

interactive(gg) + javascript(js) + save("docs/iframes/animation-line.html", minify=True)
