# Copyright 2026 Marimo. All rights reserved.

import marimo

__generated_with = "0.23.6"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    from plotnine import ggplot, aes, geom_point
    from plotnine.data import anscombe_quartet
    from ninejs import interactive, to_html

    gg = ggplot(
        data=anscombe_quartet,
        mapping=aes(x="x", y="y", color="dataset", tooltip="dataset"),
    ) + geom_point(size=4, alpha=0.7)

    html_plot = interactive(gg) + to_html()

    mo.iframe(html_plot)
    return


if __name__ == "__main__":
    app.run()
