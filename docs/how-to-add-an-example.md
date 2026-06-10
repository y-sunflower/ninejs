---
title: How to add an example
---

Documentation examples are small Python scripts that generate committed HTML
iframes. The docs pages then embed those iframes.

## Pick the right place

Use an existing guide when the example teaches one feature, such as tooltips,
CSS, JavaScript, animation, or an integration.

Use the gallery when the example is a complete chart that readers may want to
copy or adapt.

| Example type    | Source file               | Rendered HTML              | Markdown page                |
| --------------- | ------------------------- | -------------------------- | ---------------------------- |
| guide example   | `docs/examples/<slug>.py` | `docs/iframes/<slug>.html` | existing `docs/guide/*.md`   |
| gallery example | `docs/examples/<slug>.py` | `docs/iframes/<slug>.html` | new `docs/gallery/<slug>.md` |

If the example needs CSS, JavaScript, or local data, keep those support files in
`docs/examples/` too. Existing examples use names such as
`area_hover_to_show.css`, `area_hover_to_show.js`, and
`household-wealth.csv`.

## Write the Python script

Create a script in `docs/examples/`. It should run from the repository root
because `just examples` runs every file as `uv run docs/examples/<file>.py`.

Keep the script focused:

- import only what the example needs
- build one plotnine chart
- add `tooltip`, `data_id`, or `on_click` only when the example needs them
- save to `docs/iframes/<slug>.html`
- use `minify=True` so the committed iframe stays small

Template:

```py
from plotnine import aes, geom_point, ggplot, theme_minimal
from plotnine.data import mtcars

from ninejs import interactive, save


gg = (
    ggplot(mtcars, aes("wt", "mpg", tooltip="name"))
    + geom_point(size=5, alpha=0.7)
    + theme_minimal()
)

interactive(gg) + save("docs/iframes/my-example.html", minify=True)
```

If the example uses custom CSS or JavaScript, load it from `docs/examples/`:

```py
from ninejs import css, interactive, javascript, save

(
    interactive(gg)
    + css(from_file="docs/examples/my-example.css")
    + javascript(from_file="docs/examples/my-example.js")
    + save("docs/iframes/my-example.html", minify=True)
)
```

## Add the docs page

For a gallery example, create `docs/gallery/<slug>.md`.

Use a short introduction, show the code, then embed the generated iframe:

````md
---
title: My example
---

- Source: [Original chart](https://example.com)
- Author: [Original author](https://example.com)

This example shows how to use `tooltip` and `data_id` together.

```py hl_lines="4 18"
from plotnine import aes, geom_point, ggplot, theme_minimal
from plotnine.data import mtcars

from ninejs import interactive, save


gg = (
    ggplot(mtcars, aes("wt", "mpg", tooltip="name", data_id="cyl"))
    + geom_point(size=5, alpha=0.7)
    + theme_minimal()
)

interactive(gg) + save("docs/iframes/my-example.html", minify=True)
```

<iframe width="100%" height="600" src="../iframes/my-example.html" style="border:none;"></iframe>
````

The iframe path depends on where the Markdown page lives:

| Page location       | iframe path              |
| ------------------- | ------------------------ |
| `docs/index.md`     | `iframes/<slug>.html`    |
| `docs/guide/*.md`   | `../iframes/<slug>.html` |
| `docs/gallery/*.md` | `../iframes/<slug>.html` |

## Update navigation

If you added a new page, register it in `zensical.toml`.

Gallery pages go under the `Gallery` nav. Contributing pages go under the
`Contributing` nav. If you only added a new example section to an existing
guide page, the nav usually does not need to change.

For gallery examples, also add a link and iframe preview to
`docs/gallery/index.md`.

## Check the result

Run the new script first:

```bash
uv run docs/examples/my-example.py
```

Then regenerate all examples:

```bash
just examples
```

Preview the docs:

```bash
just doc
```

## Common mistakes

| Problem                                                  | What to check                                                                   |
| -------------------------------------------------------- | ------------------------------------------------------------------------------- |
| The iframe is missing                                    | The script saved to `docs/iframes/<slug>.html` and the Markdown path is correct |
| The example works locally but fails in `just examples`   | The script assumes the wrong working directory                                  |
| Custom CSS or JavaScript is not applied                  | The `from_file` path starts at the repository root                              |
| The docs page is not visible in navigation               | The page is listed in `zensical.toml`                                           |
| The iframe changed but the docs still show the old chart | Re-run the script or `just examples`                                            |
