from __future__ import annotations

from collections.abc import Mapping

from ninejs.typing import Pathish


def css_from_dict(css_dict: Mapping[str, Mapping[str, object]]) -> str:
    css: str = ""

    for selector, css_props in css_dict.items():
        css += f"{selector}{{"
        for prop, value in css_props.items():
            css += f"{prop}:{value};"
        css += "}"

    return css


def css_from_file(css_file: Pathish) -> str:
    with open(css_file, "r") as f:
        css: str = f.read()

    return css


class css:
    """
    Utility class to handle CSS injection for interactive plots.

    This class provides multiple ways to load CSS: directly from a
    string, from a dictionary, or from a CSS file. It is intended to
    be combined with `interactive` plots.

    Arguments:
        from_string: CSS rules in a string.
        from_dict: Dictionary containing
            selectors as keys and dictionaries of property-value pairs as values.
        from_file: Path to a CSS file.

    ```python
    (
        interactive(p)
        + css(".tooltip { font-size: 2rem; }")
        + css(from_dict={".tooltip": {"font-size": "2rem"}})
        + css(from_file="style.css")
        + save("output.html")
    )
    ```
    """

    def __init__(
        self,
        from_string: str | None = None,
        *,
        from_dict: Mapping[str, Mapping[str, object]] | None = None,
        from_file: Pathish | None = None,
    ) -> None:
        provided = [
            from_string is not None,
            from_dict is not None,
            from_file is not None,
        ]

        if sum(provided) != 1:
            raise ValueError(
                "Exactly one of 'from_string', 'from_dict', or 'from_file' must be provided."
            )

        if from_string is not None:
            self.css_content: str = from_string
            return

        if from_dict is not None:
            self.css_content = css_from_dict(from_dict)
            return

        assert from_file is not None
        self.css_content = css_from_file(from_file)
