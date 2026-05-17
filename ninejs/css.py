import re
import warnings


def css_from_dict(css_dict: dict) -> str:
    css: str = ""

    for selector, css_props in css_dict.items():
        css += f"{selector}{{"
        for prop, value in css_props.items():
            css += f"{prop}:{value};"
        css += "}"

    if not is_css_like(css):
        warnings.warn(f"CSS may be invalid:\n{css}")

    return css


def css_from_file(css_file: str) -> str:
    with open(css_file, "r") as f:
        css: str = f.read()

    if not is_css_like(css):
        warnings.warn(f"CSS may be invalid: {css}")
    return css


def is_css_like(s: str) -> bool:
    """
    Check whether a string looks like valid CSS. This function
    is primarly used internally, but you can use it too.

    Args:
        s: A string to evaluate.

    Returns:
        Whether or not `s` looks like valid CSS.

    Examples:
        ```python
        from plotjs import is_css_like

        is_css_like("This is not CSS.") # False
        is_css_like(".box { broken }") # False
        is_css_like(".tooltip { color: red; background: blue; }") # True
        ```
    """
    css_block_pattern = re.compile(
        r"""
        [^{]+\s*                   # Selector (at least one char that's not '{')
        \{\s*                      # Opening brace
        ([^:{}]+:\s*[^;{}]+;\s*)+  # At least one prop: value; pair
        \}                         # Closing brace
        """,
        re.VERBOSE,
    )

    matches = css_block_pattern.findall(s)
    return bool(matches)


class css:
    """
    Utility class to handle CSS injection for interactive plots.

    This class provides multiple ways to load CSS: directly from a
    string, from a dictionary, or from a CSS file. It is intended to
    be combined with `interactive` plots.

    Attributes:
        css_content (str): The CSS rules to be injected.

    Example:
        ```python
        (
            interactive(p)
            + css(".tooltip: {font-size: 2rem}")
            + css(css_from_dict={".tooltip": {"font-size": "2rem"})
            + css(from_file="style.css")
            + save("output.html")
        )
        ```
    """

    def __init__(self, from_string=None, *, from_dict=None, from_file=None):
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
            self.css_content = from_string
            return

        if from_dict is not None:
            self.css_content = css_from_dict(from_dict)
            return

        assert from_file is not None
        self.css_content = css_from_file(from_file)
