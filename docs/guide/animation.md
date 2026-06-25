---
title: Animation
---

<iframe width="100%" height="500" src="../iframes/animation.html" style="border:none;"></iframe>

`ninejs` doesn't really provide built-in animation features, but since it renders plot for the browser, it's possible to do some pretty cool things.

!!! tip

      In some cases, the following examples will require you to **refresh** the page to see the animation.

## Fade the bars

Fade the bars in one after the other when the chart loads (refresh the page to show the animation).

```py
js = """
document.querySelectorAll(".bar").forEach((bar, i) => {
   bar.style.opacity = "0";
   bar.style.transition = "opacity 0.6s ease";
   setTimeout(() => { bar.style.opacity = "1"; }, i * 200);
});
"""

interactive(gg) + javascript(js) + save("docs/iframes/javascript-animate.html")
```

<iframe width="100%" height="500" src="../iframes/javascript-animate.html" style="border:none;"></iframe>

## Line drawing

```py
from plotnine import aes, geom_line, ggplot, theme_minimal
from plotnine.data import economics

from ninejs import interactive, javascript, save

gg = (
    ggplot(
        economics.head(120),
        aes(x="date", y="unemploy", tooltip="unemploy"),
    )
    + geom_line(size=2, color="#E45756")
    + theme_minimal()
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

interactive(gg) + javascript(js) + save("docs/iframes/animation-line.html")
```

<iframe width="100%" height="500" src="../iframes/animation-line.html" style="border:none;"></iframe>

## Hover spotlight glow

```py
from plotnine import aes, geom_point, ggplot, theme_minimal
from plotnine.data import mpg

from ninejs import css, interactive, save

gg = (
    ggplot(
        mpg,
        aes(
            x="cty",
            y="hwy",
            tooltip="manufacturer",
            hover_group="manufacturer",
        ),
    )
    + geom_point(size=6, alpha=0.6, color="#F58518")
    + theme_minimal()
)

hover_css = """
.plot-element {
    transition: opacity 0.3s ease, filter 0.3s ease, transform 0.3s ease;
}

.hovered {
    filter: drop-shadow(0 0 1px purple);
    transform: scale(1.2);
}
"""

(
    interactive(gg)
    + css(hover_css)
    + save("docs/iframes/animation-hover.html")
)
```

<iframe width="100%" height="500" src="../iframes/animation-hover.html" style="border:none;"></iframe>

## Art

`ninejs` can also be used to create some piece of art 😊

```py
from plotnine import ggplot, aes, geom_point, theme_void, theme
from plotnine.data import anscombe_quartet

from ninejs import interactive, css, save

gg = (
    ggplot(data=anscombe_quartet, mapping=aes(x="x", y="y", color="dataset"))
    + geom_point(size=30, alpha=0.5)
    + theme_void()
    + theme(legend_position="none")
)

goo_css = """
svg {filter: contrast(20);}

.point {
    filter: blur(5px);
    animation: goo 3s ease-in-out infinite alternate;
}
.point:nth-child(2n) {animation-duration: 4s;}
.point:nth-child(3n) {animation-duration: 8s;}

@keyframes goo {
    from {transform: translate(-12px, -12px) scale(1);}
    to {transform: translate(12px, 12px) scale(1.3);}
}
"""

interactive(gg) + css(goo_css) + save("docs/iframes/animation-art.html")
```

<iframe width="100%" height="500" src="../iframes/animation-art.html" style="border:none;"></iframe>
